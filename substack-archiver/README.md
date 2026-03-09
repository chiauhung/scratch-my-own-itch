# Substack Archiver

Capture paywalled Substack articles as PDFs, index them into a vector database, and search them via Claude Code or Slack.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   archiver/ │───▶│  data/      │───▶│   mcp/       │◀───│ Claude Code │
│  capture +  │    │  pdf + json │    │  FastMCP +   │    └─────────────┘
│  indexer    │    └─────────────┘    │  ChromaDB    │
└─────────────┘                       └──────┬───────┘
                                             │
                                      ┌──────▼───────┐    ┌─────────────┐
                                      │ slack-agent/ │◀───│    Slack    │
                                      │  ADK + Bolt  │    └─────────────┘
                                      └──────────────┘
```

## Folders

| Folder | What it does |
|--------|-------------|
| [`archiver/`](./archiver/) | Playwright capture + ChromaDB indexer |
| [`mcp/`](./mcp/) | FastMCP server — semantic search over the archive |
| [`slack-agent/`](./slack-agent/) | ADK agent + Slack bot (Socket Mode) |

## Quick Start

```bash
# Install dependencies
uv sync
uv run playwright install webkit

# Start Docker services (ChromaDB + MCP server)
docker-compose up -d chromadb mcp-server

# Capture an article
uv run archiver/capture.py "https://example.substack.com/p/article" --login

# Index into ChromaDB
uv run archiver/indexer.py
```

See each folder's README for detailed usage.

## Stack

`Python` · `Playwright` · `ChromaDB` · `FastMCP` · `Google ADK` · `Slack Bolt` · `Docker` · `uv`
