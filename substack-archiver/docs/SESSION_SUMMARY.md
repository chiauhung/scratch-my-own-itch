# Session Summary - Substack Newsletter Archiver + MCP Search

## Project Overview

A complete solution for capturing Substack newsletters as PDFs and searching them via Claude Code using Model Context Protocol (MCP).

## What We Built

### 1. PDF Capture System
- **Playwright-based** web scraper using Safari (webkit)
- **Persistent login sessions** to bypass paywalls
- **Viewport-by-viewport capture** for perfect pagination
- **Text extraction** from DOM (even from paywalled content)
- Saves both **PDF** (visual archive) and **JSON** (search index)

### 2. Vector Search Engine
- **ChromaDB** for semantic search over newsletter archive
- **FastMCP HTTP server** for Claude Code integration
- **500-character excerpts** to minimize token usage
- **Docker-based deployment** for portability

### 3. MCP Integration
- HTTP MCP server on `localhost:8001`
- Single tool: `search_substacks(query, n_results)`
- Integrated with Claude Code via `~/.claude.json` config
- PDF paths included for reference (but not read by AI)

## Architecture

```
┌─────────────────┐
│ Capture Phase   │
└─────────────────┘
    Playwright → Login → Reload → Extract Text → Capture Screenshots
         ↓                              ↓                    ↓
    .playwright_session/          data/json/           data/pdf/

┌─────────────────┐
│ Indexing Phase  │
└─────────────────┘
    data/json/ → Indexer → ChromaDB → chroma_data/

┌─────────────────┐
│ Search Phase    │
└─────────────────┘
    Claude Code → HTTP MCP (port 8001) → FastMCP Server → ChromaDB
                       ↓
              500-char excerpts + metadata
                       ↓
              AI-powered answers with citations
```

## Key Technical Decisions

### 1. Switched from GLM API to MCP Server
**Problem**: GLM API returned empty responses, required coding endpoint
**Solution**: Built FastMCP server, let Claude Code handle Q&A
**Benefits**:
- Uses existing Claude Code subscription
- Better context understanding
- No API key management
- No rate limits

### 2. HTTP MCP (not stdio)
**Reason**: Match user's existing MCP servers (Jira, BigQuery)
**Config**:
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

### 3. Page Reload After Login
**Problem**: Text extraction happened before login, captured paywall content
**Solution**: Added `page.reload(wait_until="networkidle")` after login
**Result**: Full article content extracted even from paywalled posts

### 4. Concise Excerpts (500 chars)
**Problem**: Returning full documents would waste tokens
**Solution**: Return only 500-char excerpts per article
**Docstring Instruction**: Added "DO NOT read PDF files" to tool description

### 5. Separate Cache Volumes
**Structure**:
- `chroma_data/` - ChromaDB vector database
- `mcp_cache/` - ONNX embedding models
**Benefits**: Clean separation, no re-downloads on restart

## File Structure

```
substack-playwright/
├── src/
│   ├── capture.py           # Playwright PDF capture + text extraction
│   ├── indexer.py           # Index JSON files to ChromaDB
│   └── mcp_server.py        # FastMCP HTTP server
├── docker-compose.yml        # ChromaDB + MCP server
├── pyproject.toml           # Dependencies (uv)
├── index.sh                 # Indexing convenience script
├── data/
│   ├── pdf/                 # Generated PDFs
│   └── json/                # Text content for search
├── chroma_data/             # ChromaDB vector storage
├── mcp_cache/               # ONNX model cache
└── .playwright_session/     # Browser login session
```

## How to Use

### Setup (One-time)
```bash
# 1. Install dependencies
uv sync
uv run playwright install webkit

# 2. Start Docker services
docker-compose up -d

# 3. Configure Claude Code
# Add to ~/.claude.json:
{
  "mcpServers": {
    "substack-search": {
      "type": "http",
      "url": "http://localhost:8001/mcp"
    }
  }
}

# 4. Restart Claude Code
```

### Daily Workflow
```bash
# 1. Capture articles (first time with --login)
uv run src/capture.py "https://example.substack.com/p/article" --login

# 2. Index new articles
./index.sh

# 3. Search in Claude Code
"Search my substacks for 'topic'"
```

## Key Fixes Made

### Issue 1: MCP Server Config Schema Error
**Error**: "Does not adhere to MCP server configuration schema"
**Fixes**:
1. Initially tried: `"url": "http://localhost:8001/sse"` (❌ 404)
2. Then tried: `"url": "http://localhost:8001/mcp/sse"` (❌ 404)
3. Finally: `"type": "http", "url": "http://localhost:8001/mcp"` (✅)

### Issue 2: Paywall Content Extracted
**Error**: JSON contained paywall text instead of full article
**Cause**: Text extraction happened before login
**Fix**: Added page reload after login wait
```python
if login_wait:
    input()  # Wait for manual login
    page.reload(wait_until="networkidle")  # Reload to get full content
```

### Issue 3: Claude Code Reading PDFs
**Error**: AI tried to read PDF files, wasting tokens
**Fix**: Updated tool docstring with explicit instructions:
```python
"""
IMPORTANT: The excerpts returned contain ALL the information needed to answer
the user's question. DO NOT attempt to read or access the PDF files listed
in the results - they are for reference only. Use only the text excerpts
provided in the search results.
"""
```

### Issue 4: ONNX Model Re-downloads
**Issue**: MCP server re-downloaded models on every restart
**Fix**: Added cache volume mount
```yaml
volumes:
  - ./mcp_cache:/root/.cache
```

## Technology Stack

- **Playwright** - Browser automation
- **Pillow** - Image/PDF processing
- **ChromaDB** - Vector database
- **FastMCP** - MCP server framework
- **Docker** - Service containerization
- **uv** - Fast Python package manager
- **Safari (webkit)** - Browser engine
- **Claude Code** - AI coding assistant

## Performance Characteristics

### Capture
- ~10 seconds per article (depends on length)
- ~1-2 MB per PDF
- ~10-50 KB per JSON

### Indexing
- ~1 second per article
- Embedding generation via ChromaDB default function

### Search
- ~100-500ms per query
- Returns top N results (default 3, max 10)
- 500 chars × N results = minimal token usage

## Configuration Files

### docker-compose.yml
```yaml
services:
  chromadb:
    image: chromadb/chroma:latest
    ports: ["8000:8000"]
    volumes: ["./chroma_data:/chroma/chroma"]

  mcp-server:
    image: ghcr.io/astral-sh/uv:python3.13-bookworm-slim
    command: ["uv", "run", "src/mcp_server.py"]
    ports: ["8001:8001"]
    volumes:
      - ./src:/app/src
      - ./pyproject.toml:/app/pyproject.toml
      - ./uv.lock:/app/uv.lock
      - ./mcp_cache:/root/.cache
    environment:
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
```

### ~/.claude.json
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

## Future Enhancements

### Capture
- [ ] Batch capture from Substack feed RSS
- [ ] Support for other newsletter platforms
- [ ] Configurable viewport size
- [ ] OCR for images in articles

### Search
- [ ] Web UI for search
- [ ] Multiple ChromaDB collections
- [ ] Configurable excerpt length
- [ ] Export search results
- [ ] Full-text search (in addition to semantic)

### MCP
- [ ] Additional tools (list all articles, get article by URL, etc.)
- [ ] Streaming responses for long answers
- [ ] Search filters (date range, author, etc.)

## Success Metrics

✅ **MCP server working** - Successfully integrated with Claude Code
✅ **Full content extraction** - Bypasses paywalls via login session
✅ **Token-efficient** - 500-char excerpts instead of full documents
✅ **Docker-based** - Easy deployment and portability
✅ **Persistent storage** - Login sessions, vector DB, and cache all persist
✅ **Clean architecture** - Separate concerns (capture, index, search)

## Lessons Learned

1. **MCP HTTP vs SSE**: FastMCP with streamable-http uses HTTP transport, not SSE endpoint
2. **Schema validation**: MCP config requires `"type": "http"` explicitly
3. **Timing matters**: Page reload after login is critical for full content extraction
4. **Tool instructions**: Explicit docstring instructions prevent AI from reading PDFs
5. **Cache management**: Separate volumes for different types of cached data

## Final State

**Services Running**:
- ChromaDB on `localhost:8000`
- MCP Server on `localhost:8001`

**Health Checks**:
```bash
curl http://localhost:8001/health_check  # Should return "OK"
docker ps | grep mcp-server              # Should show running container
```

**Test Search**:
In Claude Code: `"Search my substacks for 'topic'"`

## Project Complete ✅

All goals achieved:
1. ✅ Capture Substack articles as PDFs with text extraction
2. ✅ Bypass paywalls via login session persistence
3. ✅ Index articles for semantic search
4. ✅ MCP server integration with Claude Code
5. ✅ Token-efficient search with concise excerpts
6. ✅ Docker-based deployment
7. ✅ Comprehensive documentation

---

**Session End**: 2026-01-29
**Status**: Production Ready 🚀
