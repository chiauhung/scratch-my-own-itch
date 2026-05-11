# Vector Store Alternatives

The substack-archiver uses **ChromaDB** for semantic search over the article archive. This doc compares it against two alternatives — **LanceDB** and **FAISS** — and explains why ChromaDB won for this project's specific needs.

The project is single-user, runs locally, holds on the order of hundreds-to-low-thousands of articles, and exposes search through an MCP server consumed by Claude Code.

## At a glance

| Aspect | ChromaDB (current) | LanceDB | FAISS |
|--------|--------------------|---------|-------|
| Architecture | HTTP client + server | Embedded library | Embedded library |
| Setup | `docker-compose up` | `pip install lancedb` | `pip install faiss-cpu` |
| Storage | Server-managed volume | Local files, S3, or GCS | Manual file save/load |
| Embeddings | Built-in (server-side default) | Bring-your-own (e.g. fastembed) | Bring-your-own (always) |
| Metadata filtering | Yes, dict-based at query time | Yes, SQL-style on PyArrow schema | None — bring a sidecar store |
| Persistence | Automatic via container volume | Files on disk / object store | Manual `write_index` / `read_index` |
| Concurrent writers | Yes (server arbitrates) | No (single-writer) | No (no concurrency model) |
| Best for | Quick prototyping, multi-client | Serverless deploys, batch pipelines | Raw speed, library-level integration |

## Why ChromaDB for this project

- **MCP server runs in Docker anyway** — adding a sidecar container is free. The "no server needed" benefit of embedded stores doesn't apply when the rest of the stack is already containerised.
- **Default embeddings work out of the box** — no need to pick a model, manage a download, or wire fastembed in. For a personal archive, the default ONNX MiniLM is fine.
- **Metadata filtering via dicts** — the `search_substacks` MCP tool can grow date or author filters later without a schema migration.

## When LanceDB would be the better pick

- **If the MCP server moved to a serverless target** (Cloud Run, Lambda). LanceDB reading from GCS/S3 in-process removes the always-on ChromaDB container.
- **If the archive grew to tens of thousands of articles** and you wanted explicit schema control for filtered search performance.
- **If indexing moved to a batch job** (e.g. nightly cron) rather than the current ad-hoc `uv run archiver/indexer.py` — LanceDB's embedded model fits batch pipelines well.

Downside for this project: bringing your own embedding model (fastembed) is one more thing to manage, and the docker-compose stack already absorbs ChromaDB's setup cost.

## When FAISS would be the better pick

- **If raw query latency mattered more than ergonomics** — FAISS is the fastest of the three and the underlying index type ChromaDB and LanceDB benchmark against.
- **If the search was embedded inside another Python process** (no MCP server, no Docker) — `faiss.IndexFlatIP` plus a pickled list of metadata is genuinely the simplest possible setup.

Downside for this project: no metadata, no persistence, no IDs. You'd reinvent a thin wrapper around `faiss.write_index` + a SQLite sidecar for article URLs/dates/excerpts. That's exactly what ChromaDB and LanceDB already provide. Not worth it for hundreds of documents queried at human speeds.

## Decision summary

For substack-archiver as it stands today: **ChromaDB stays**. The Docker stack already pays its setup cost, default embeddings remove a decision, and metadata filtering is there when needed. LanceDB becomes attractive if this ever moves to a serverless deploy; FAISS only makes sense if the whole architecture collapses into a single Python process.

---

## Appendix — LanceDB implementation patterns

Notes from reading `confluence_embedding/core.py` in `de-integration-cf`. Kept here in case substack-archiver does eventually migrate to LanceDB.

### Explicit embedding with fastembed

```python
from fastembed import TextEmbedding

model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
vectors = [e.tolist() for e in model.embed(texts)]
```

Model runs locally in-process, no external API calls. Singleton pattern via `_get_model()` avoids reloading on each indexing call.

### Typed PyArrow schema

```python
pa.schema([
    pa.field("page_id", pa.string()),
    pa.field("chunk_index", pa.int32()),
    pa.field("content", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 384)),
])
```

Enforces structure at write time and enables filtered search (`space_key = 'ENG'`-style predicates).

### Heading-aware chunking

Splits markdown by headings and preserves the hierarchy as a breadcrumb prefix:

```
"Section > Subsection\n\nbody text"
```

Each chunk carries its own context. Falls back to paragraph splitting (~200 words) for pages without headings. This is the biggest retrieval-quality win regardless of which vector store is underneath — applies equally well to the current ChromaDB setup.

### Upsert = delete + add

```python
table.delete(f"page_id = '{page_id}'")
table.add(records)
```

One source document produces multiple chunks, so a single-row upsert doesn't work. Delete all chunks for the page, then re-add — clean and idempotent.

### How LanceDB persists

- No server process — the Python library reads/writes storage directly
- `lancedb.connect("gs://bucket/path/")` opens GCS files in-process, no HTTP calls
- Same mental model as DuckDB reading Parquet, but for vector search over Lance-format files
- Tradeoff: no concurrent multi-writer support (fine for batch jobs, not for multi-user apps)
