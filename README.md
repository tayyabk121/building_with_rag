# Building with RAG

FastAPI seed for the classroom RAG capstone. See `docs/architecture.md`.

## Run

```
uv sync
uv run uvicorn building_with_rag.main:app --port 8000
```

## Configuration notes

- Copy `.env.example` to `.env`. `.env` is untracked; never commit secrets.
- `GENERATION_API_BASE_URL` / `GENERATION_API_KEY`: supplied by the trainer for an OpenAI-compatible LiteLLM proxy. Leave blank until Story 3.1.
- `MONGODB_URI`: Atlas free-tier (M0) connection string. The Atlas IP access list must allow your machine.
- A free Voyage key is rate limited, so Story 2.2 embedding takes about 40 minutes.
