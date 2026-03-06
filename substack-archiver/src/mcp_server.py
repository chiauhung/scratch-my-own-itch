#!/usr/bin/env python3
"""
Substack Search MCP Server (using FastMCP)
Provides semantic search over your Substack newsletter archive
"""

import logging
import traceback

import chromadb
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Create FastMCP server
mcp = FastMCP("Substack Search")

# Connect to ChromaDB (read from environment variable for Docker)
import os
chroma_host = os.getenv("CHROMA_HOST", "localhost")
chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)


@mcp.custom_route(path="/health_check", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Perform a health check on the service.

    Args:
        request: The incoming request object.

    Returns:
        PlainTextResponse: A response indicating the service status.
    """
    return PlainTextResponse("OK")


@mcp.tool()
def search_substacks(query: str, n_results: int = 3) -> str:
    """Search your Substack newsletter archive for relevant articles.

    Fetches articles from ChromaDB using semantic search and returns
    concise excerpts from the most relevant articles. This tool provides
    information to answer questions about your Substack newsletter archive.

    IMPORTANT: The excerpts returned contain ALL the information needed to answer
    the user's question. DO NOT attempt to read or access the PDF files listed
    in the results - they are for reference only. Use only the text excerpts
    provided in the search results.

    When answering, ALWAYS include a "Sources:" section at the end citing:
    - Article title
    - PDF path (so user can open the file)

    Note:
        - Returns only the first 500 characters of each article as excerpts
        - Use with caution for large result sets
        - PDF paths are for reference only - DO NOT read the PDF files

    Args:
        query: Search query (natural language question or keywords)
        n_results: Number of results to return (default: 3, max: 10)

    Returns:
        str: Formatted search results with article excerpts and metadata,
             or an error message if search fails.

    Raises:
        Exception: If an unexpected error occurs during the search process.
    """
    # Limit n_results
    n_results = min(max(n_results, 1), 10)

    try:
        # Get collection
        collection = chroma_client.get_collection("substacks")

        # Search (include distances for relevance filtering)
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        if not results['documents'][0]:
            logging.info(
                msg={
                    "event": "No results found for query",
                    "payload": {"query": query, "n_results": n_results},
                }
            )
            return "No relevant articles found in your Substack archive."

        # Filter by relevance threshold (lower distance = more relevant)
        # Typical threshold: 1.0-1.5 for good matches, adjust based on your data
        RELEVANCE_THRESHOLD = 1.2

        # Format results - return CONCISE excerpts only
        formatted_results = []
        for i, (doc, meta, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            # Skip results that are too dissimilar
            if distance > RELEVANCE_THRESHOLD:
                continue
            # Extract only the most relevant excerpt (first 500 chars)
            excerpt = doc[:500].strip()
            if len(doc) > 500:
                excerpt += "..."

            formatted_results.append(
                f"[{len(formatted_results) + 1}] **{meta.get('title', 'Untitled')}** (relevance: {1 - distance:.2f})\n"
                f"Author: {meta.get('author', 'Unknown')} | "
                f"Date: {meta.get('date', 'N/A')[:10]}\n"
                f"URL: {meta.get('url', 'N/A')}\n"
                f"PDF: {meta.get('pdf_path', 'N/A')}\n\n"
                f"Excerpt:\n{excerpt}\n"
            )

        if not formatted_results:
            return f"No sufficiently relevant articles found for: \"{query}\". Try a different search query."

        result_text = (
            f"Found {len(formatted_results)} relevant article(s) for: \"{query}\"\n\n"
            + "\n---\n\n".join(formatted_results)
        )

        logging.info(
            msg={
                "event": "Successfully retrieved search results",
                "payload": {
                    "query": query,
                    "n_results": len(formatted_results),
                },
            }
        )

        return result_text

    except Exception as e:
        logging.error(
            msg={
                "event": "Search failed",
                "error": str(e),
                "payload": {"traceback": traceback.format_exc()},
            }
        )
        return (
            f"Error searching substacks: {str(e)}\n\n"
            f"Make sure ChromaDB is running (docker-compose up -d) "
            f"and articles are indexed (./index.sh)"
        )


if __name__ == "__main__":
    # Run as HTTP server on localhost:8001 (like Jira, BigQuery MCP servers)
    mcp.run(transport="streamable-http", port=8001, host="0.0.0.0")
