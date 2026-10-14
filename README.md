# ai-service-py — FastAPI service for AI workloads

A Python counterpart to my JVM AI services, built to explore where each stack fits best.
Async-first, strictly typed, tested without network access.

> Work in progress. Companion project to
> [ai-backend-playground](https://github.com/NazirovJr/ai-backend-playground) (Spring Boot + Spring AI).

---

## Stack

| Layer | Choice |
|---|---|
| Runtime | Python 3.13 |
| Web framework | FastAPI (ASGI) |
| HTTP client | httpx (async, pooled) |
| Validation & config | Pydantic v2, pydantic-settings |
| LLM | Ollama (local models) |
| Tooling | uv, ruff, mypy `--strict`, pytest |

---

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /health/check` | Liveness probe with version |
| `POST /api/v1/chunker` | Split text into overlapping chunks (RAG preprocessing) |
| `POST /api/v1/fetch/all` | Fetch multiple URLs **concurrently**, degrading per-source |
| `POST /api/v1/stream` | Stream LLM tokens over Server-Sent Events |

Interactive docs at `/docs` when `APP_DEBUG=true`.

---

## Architecture

Dependencies point one way only — the domain never imports FastAPI.

```
main.py          app assembly, lifespan, router registration
  ├─ routes/     HTTP layer: status codes, headers, Depends
  ├─ deps.py     dependency providers only
  ├─ schemes.py  Pydantic request/response models
  ├─ domain/     pure logic — no framework imports
  └─ client/     external API wrappers
```

**Verification that layers hold:** every function in `domain/` is callable from a plain
script with no application running. `tests/test_parallel.py` does exactly that.

---

## Design decisions

### 1. One HTTP client per process, created in `lifespan`

A client per request means a fresh TCP connection and TLS handshake every time, and
leaks sockets in `TIME_WAIT` until the process runs out of file descriptors. The client
is created once at startup with explicit pool limits and injected via `Depends`.

### 2. Dependencies are passed as arguments, not created inside

`fetch_all(urls, client)` receives the client rather than constructing it. Consequence:
tests need no monkeypatching — they pass a `MockTransport` client directly. Decoupling
simplified the tests instead of complicating them.

### 3. Validation pushed to the system boundary

`overlap >= chunk_size` is rejected by a Pydantic `model_validator` **before** the domain
runs, so the client gets a descriptive **422** and the domain's `ValueError` never becomes
a 500. Invalid input dies as early as possible.

### 4. Failures degrade per source, cancellation propagates

`fetch_all` uses `asyncio.gather(return_exceptions=True)`: one dead URL does not sink the
batch. But `CancelledError` inherits from `BaseException`, not `Exception`, and is
**re-raised** — swallowing it breaks task cancellation and graceful shutdown.

### 5. Streaming errors are reported in-band

Once SSE headers are sent, the HTTP status cannot change. Errors are emitted as an
`event: error` frame rather than silently truncating the stream, so the client can tell
failure apart from completion. Client disconnects are detected with
`await request.is_disconnected()` to stop paying for unused tokens.

### 6. Config has exactly one source

All settings live in a single `Settings` class with `extra="forbid"`: a typo in an
environment variable fails the process at startup instead of being silently ignored.

---

## Running

```bash
uv sync
cp .env.example .env
uv run uvicorn ai_service_py.main:app --reload
```

Requires [Ollama](https://ollama.com) for the streaming endpoint:

```bash
ollama pull qwen3-coder-next-agent
```

## Quality gates

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -q
```

Tests use `httpx.MockTransport` and `ASGITransport` — no network, no server, no flakiness.

---

## Roadmap

- [ ] RAG endpoint with pgvector
- [ ] Cross-encoder reranking service (callable from the JVM project)
- [ ] Evaluation harness with a golden dataset
- [ ] Prometheus metrics, including LLM token accounting
- [ ] Dockerfile and CI pipeline
