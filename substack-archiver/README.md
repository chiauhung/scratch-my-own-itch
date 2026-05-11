# Substack Archiver

Capture paywalled Substack articles as PDFs, index them into a vector database, and search them via Claude Code.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   archiver/ │───▶│  data/      │───▶│   mcp/       │◀───│ Claude Code │
│  capture +  │    │  pdf + json │    │  FastMCP +   │    └─────────────┘
│  indexer    │    └─────────────┘    │  ChromaDB    │
└─────────────┘                       └──────────────┘
```

## Folders

| Folder | What it does |
|--------|-------------|
| [`archiver/`](./archiver/) | Playwright capture + ChromaDB indexer |
| [`mcp/`](./mcp/) | FastMCP server — semantic search over the archive |

## Quick Start

```bash
# Install dependencies
uv sync
uv run playwright install webkit

# Start Docker services (ChromaDB + MCP server)
docker-compose up -d chromadb mcp-server

# Capture an article (ChromaDB not needed yet — saves to data/ locally)
uv run archiver/capture.py "https://example.substack.com/p/article" --login

# Index into ChromaDB (ChromaDB must be running first)
uv run archiver/indexer.py
```

See each folder's README for detailed usage.

## Stack

`Python` · `Playwright` · `ChromaDB` · `FastMCP` · `Docker` · `uv`
