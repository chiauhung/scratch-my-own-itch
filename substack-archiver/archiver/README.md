# Archiver

Captures Substack articles as paginated PDFs and indexes them into ChromaDB for semantic search.

## Capture

**First time (paywalled content):**
```bash
./capture.sh "https://example.substack.com/p/article" --login
```
Browser opens → log in manually → press ENTER → PDF + JSON saved to `data/`.

**Subsequent captures (session reused):**
```bash
./capture.sh "https://example.substack.com/p/article"
```

**Options:**
```bash
-o my_name.pdf   # custom filename
--headless       # no browser window
--login          # pause for manual login
```

Login session persists in `.playwright_session/` until cookies expire.

## Index

After capturing, index into ChromaDB:
```bash
./index.sh
```

Reads all JSONs from `data/json/`, embeds and upserts into ChromaDB. Safe to re-run — existing documents are updated, not duplicated.

## Output

```
data/
├── pdf/    ← paginated PDF (each viewport = 1 page)
└── json/   ← text content + metadata for search indexing
```

## Troubleshooting

- **Paywall content missing**: Use `--login` on first capture, wait for full page load before pressing ENTER
- **Lazy-loaded content cut off**: Increase `wait_for_timeout` in `capture.py`
- **ChromaDB connection refused**: Run `docker-compose up -d chromadb` first
