# Document Agent Demo

A small, deployable demonstration of two complementary enterprise-knowledge capabilities:

1. **Structured catalog retrieval** - deterministic filters for lifecycle stage, topic and effective date, including an `All` wildcard.
2. **Text-based PDF extraction** - page-level text blocks, native table rows and bounding boxes (`bbox`) returned as JSON.

It intentionally contains **no private documents, company names, credentials, customer data, or external model keys**. Uploaded PDFs are processed in memory and are not written to disk.

## Why not use only RAG?

Semantic RAG is useful for questions about what a document says. It is less reliable for strict filters such as "documents for the Build stage, related to Security, effective after a date." This demo shows a hybrid foundation:

```text
Structured filtering → deterministic, auditable document selection
PDF extraction       → clean content for chunking, RAG and citations
Agent routing        → select the appropriate tool for a user question
```

## Features

- FastAPI API with OpenAPI documentation at `/docs`
- Browser demo for catalog search and PDF extraction
- In-memory PDF processing with a 12 MB upload limit
- Public synthetic catalog data only
- Configuration through environment variables (`DOCUMENT_AGENT_*`)
- API tests for PDF extraction and validation, plus Ruff and Mypy quality checks
- Dockerfile, Docker Compose and GitHub Actions CI

## Run locally

Requires Python 3.11+.

```bash
git clone https://github.com/<your-username>/document-agent-demo.git
cd document-agent-demo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://localhost:8000>. API documentation is available at <http://localhost:8000/docs>.

Optional runtime configuration:

```bash
export DOCUMENT_AGENT_MAX_PAGES=20
export DOCUMENT_AGENT_LOG_LEVEL=DEBUG
```

## Run with Docker

```bash
docker compose up --build
```

## API examples

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'content-type: application/json' \
  -d '{"lifecycle_stage":"Build","topic":"Security"}'

curl -X POST http://localhost:8000/api/parse \
  -F 'file=@example.pdf'
```

## Deployment

The repository is ready for any Docker-compatible host. Configure the service command as:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For a public demo, keep the default upload limit, do not add internal PDFs, and use environment variables for any future model API key.

## Scope and next steps

This is intentionally a compact demo, not a production compliance system. Useful extensions include OCR for scanned PDFs, persistent storage, authentication, rate limiting, a vector database, reranking, source citations and an MCP server for tool-based agents.
