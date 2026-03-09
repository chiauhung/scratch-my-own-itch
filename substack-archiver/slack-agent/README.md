# Slack Agent

ADK-powered Slack bot that answers questions about your Substack archive.
Mention the bot in Slack → it searches ChromaDB via MCP → replies with cited articles.

## Architecture

```
Slack
  ↓  Socket Mode (WebSocket)
slack-bot  (Slack Bolt — this folder)
  ↓  HTTP
adk-agent  (ADK api_server)
  ↓  MCP tool call
mcp-server (FastMCP — ../mcp/)
  ↓  query
chromadb   (vector search — ../docker-compose.yml)
```

Session continuity: Slack `thread_ts` → ADK `session_id`, stored in SQLite (`data/sessions.db`).

## Quick Start

### 1. Create a Slack App

At https://api.slack.com/apps:
- Enable **Socket Mode** → generate App-Level Token (`xapp-...`) with `connections:write` scope
- Add Bot Token Scopes: `app_mentions:read`, `chat:write`
- Enable **Event Subscriptions** → subscribe to `app_mention`
- Install app to workspace → copy Bot Token (`xoxb-...`)

### 2. Configure environment

```bash
cp slack-agent/.env.example slack-agent/.env
# Fill in SLACK_BOT_TOKEN, SLACK_APP_TOKEN, GOOGLE_API_KEY
```

### 3. Start all services

```bash
# Make sure ChromaDB is indexed first
./index.sh

# Start everything
docker-compose up -d
```

### 4. Use it

Mention the bot in any channel it's in:
```
@substack-bot what did the author say about DuckDB?
@substack-bot summarise the articles about data engineering
```

## Production Gaps

This is a local demo. Here's what changes for production:

| Local | Production | Notes |
|-------|-----------|-------|
| Socket Mode | Events API (HTTPS webhook) | Requires public URL (Cloud Run / Cloud Function) |
| No signature check | `SignatureVerifier` (HMAC-SHA256) | Critical — reject all unverified requests |
| No retry handling | Check `X-Slack-Retry-Num` header | Return 200 immediately to prevent duplicate processing |
| SQLite | Firestore | Distributed, TTL-based session expiry, survives restarts |
| `adk api_server` in Docker | Vertex AI Agent Engine | Managed runtime, auto-scaling, no infra to maintain |
| No MCP auth | GCP IAM / OIDC tokens | Service-to-service auth via `GCPAuthMCPToolset` |
| Buffered reply | `chat_stream()` | Streams agent response chunks to Slack in real-time |
| `logging` | Langfuse + Cloud Logging | LLM observability, prompt versioning, usage tracking |

## File Structure

```
slack-agent/
├── substack_search_agent/   ← ADK app (dir name = app_name in API calls)
│   └── agent.py             ← LlmAgent with MCPToolset, defines root_agent
├── slack_bot/
│   ├── app.py               ← Slack Bolt Socket Mode bot
│   └── session.py           ← SQLite session store (thread_ts → session_id)
├── data/                    ← Generated: sessions.db
├── pyproject.toml
├── .env.example
└── README.md
```
