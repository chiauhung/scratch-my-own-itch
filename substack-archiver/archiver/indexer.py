#!/usr/bin/env python3
"""
Index Substack JSON files into ChromaDB for semantic search
Run this after capturing new Substack articles
"""

import chromadb
import json
import os
import re
from glob import glob
from pathlib import Path


def clean_substack_content(content: str) -> str:
    """
    Clean Substack article content before indexing.

    Removes:
    - Paywall prompts (subscription CTAs)
    - Discount/trial mentions
    - Repeated boilerplate text

    Args:
        content: Raw article text content

    Returns:
        Cleaned content ready for indexing
    """
    if not content:
        return content

    # Patterns to remove (Vu Trinh's Substack specific, but common across Substack)
    # Note: Using [''\u2019] to match straight apostrophe and RIGHT SINGLE QUOTATION MARK (U+2019)
    apos = r"[''\u2019]"  # Matches ' or ' or '

    patterns_to_remove = [
        # Paywall subscription prompts (Vu Trinh specific)
        r"I invite you to join my paid membership list to read this writing and \d+\+ high-quality data engineering articles:\s*\n*",
        r"Upgrade subscription\s*\n*",
        rf"If that price isn{apos}t affordable for you, check this DISCOUNT\s*\n*",
        rf"If you{apos}re a student with an education email, use this DISCOUNT\s*\n*",
        r"You can also claim this post for free \(one post only\)\.\s*\n*",
        rf"Or take the 7-day trial to get a feel for what you{apos}ll be reading\.\s*\n*",

        # Generic Substack CTAs
        r"Subscribe\s+to\s+continue\s+reading\.?\s*\n*",
        r"This\s+post\s+is\s+for\s+paid\s+subscribers\.?\s*\n*",
        r"Already\s+a\s+paid\s+subscriber\?\s*Sign\s+in\.?\s*\n*",
        r"Subscribe\s+now\.?\s*\n*",

        # Share/like buttons text (be careful with these - only standalone)
        r"^Share this post\s*$",
        r"^Share\s*$",
        r"^Like\s*Comment\s*Share\s*$",
    ]

    cleaned = content
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)

    # Remove excessive whitespace (multiple newlines become double newline)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def index_substacks(data_dir=None, chroma_host="localhost", chroma_port=8000):
    """
    Load all JSON files from data/json/ directory into ChromaDB

    Args:
        data_dir: Directory containing JSON files (default: data/json relative to project root)
        chroma_host: ChromaDB host
        chroma_port: ChromaDB port
    """
    # Get project root (parent of src/)
    project_root = Path(__file__).parent.parent

    # Default to data/json in project root
    if data_dir is None:
        data_dir = project_root / "data" / "json"
    else:
        # If user provides a path, convert to Path object
        data_dir = Path(data_dir)
        # If it's relative, make it relative to project root
        if not data_dir.is_absolute():
            data_dir = project_root / data_dir

    print(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}...")
    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

    # Get or create collection
    collection = client.get_or_create_collection(
        name="substacks",
        metadata={"description": "Substack newsletter articles"}
    )

    print(f"Collection 'substacks' ready")

    # Find all JSON files
    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {data_dir}/")
        print(f"Run the capture script first: ./capture.sh [URL]")
        return

    print(f"Found {len(json_files)} JSON files")

    # Track stats
    added = 0
    updated = 0
    skipped = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            raw_content = data.get('content', '')

            if not raw_content:
                print(f"⚠️  Skipping {json_file} - no content")
                skipped += 1
                continue

            # Clean content before indexing
            content = clean_substack_content(raw_content)

            # Use URL as unique ID
            doc_id = metadata.get('url', '')
            if not doc_id:
                print(f"⚠️  Skipping {json_file} - no URL in metadata")
                skipped += 1
                continue

            # Check if document already exists
            existing = collection.get(ids=[doc_id])

            if existing['ids']:
                # Update existing document
                collection.update(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[metadata]
                )
                print(f"✓ Updated: {metadata.get('title', 'Untitled')}")
                updated += 1
            else:
                # Add new document
                collection.add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[metadata]
                )
                print(f"✓ Added: {metadata.get('title', 'Untitled')}")
                added += 1

        except Exception as e:
            print(f"❌ Error processing {json_file}: {e}")
            skipped += 1

    print("\n" + "="*60)
    print("Indexing complete!")
    print(f"Added: {added} | Updated: {updated} | Skipped: {skipped}")
    print(f"Total documents in collection: {collection.count()}")
    print("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Index Substack JSON files into ChromaDB"
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Directory containing JSON files (default: data/json in project root)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="ChromaDB host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="ChromaDB port (default: 8000)"
    )

    args = parser.parse_args()
    index_substacks(args.data_dir, args.host, args.port)
