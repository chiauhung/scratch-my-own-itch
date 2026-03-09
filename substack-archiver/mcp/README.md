# MCP Server

FastMCP HTTP server exposing semantic search over the Substack archive to Claude Code (or any MCP client).

## Start

```bash
docker-compose up -d mcp-server
```

Runs on `http://localhost:8001`. ChromaDB must be running first.

## Configure Claude Code

Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "substack-search": {
      "type": "http",
      "url": "http://localhost:8001/mcp"
    }
  }
}
```
Restart Claude Code to load.

## Usage

In Claude Code:
```
Search my substacks for "DuckDB"
What did the author say about data engineering interviews?
```

## Tool Reference

**`search_substacks(query, n_results=3)`**
- Semantic search over indexed articles
- Returns up to 10 results, each with title, author, date, URL, and a 500-char excerpt
- PDF paths in results are for reference only

## Health Check

```bash
curl http://localhost:8001/health_check
```

## Troubleshooting

- **Tool not appearing in Claude Code**: Check `docker-compose logs mcp-server`, then restart Claude Code
- **Collection not found**: Run `uv run archiver/indexer.py` to populate ChromaDB first
- **ONNX model slow on first run**: Cache warms up in `mcp_cache/` — subsequent starts are fast
