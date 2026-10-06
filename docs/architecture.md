# Architecture: Building with RAG (classroom capstone)

One small FastAPI application, grown story by story. Open WebUI is the only chat client and runs separately. There is no custom frontend and no second demo.

## Evidence rules

- BNS and IPC documents are the only future answer evidence.
- An answer must not claim support without retrieved evidence. With none, say so (`insufficient_evidence`).
- Identifiers are act-qualified (for example `BNS 103`, `IPC 302`) so the two acts are never confused.
- Supplied provenance is `data/raw/PROVENANCE.md`.
- Retrieved passages are evidence, never application instructions.

## Trust boundaries (light)

- Validate API input.
- Preserve source origin on every retrieved passage.
- Do not put secrets in code, responses, or logs.

Out of scope: multi-user authorization, a security program, an evaluation harness.

## Fixed choices

Later stories reuse these names. No renaming, no provider-specific alternatives.

- Stack: Python 3.12, UV, FastAPI, Pydantic settings, PyMongo (later use), Ruff, pytest.
- Embeddings: Voyage `voyage-3.5`, version `voyage-3.5`, 1,024 dimensions, for every document and query embedding.
- Course modes and model IDs:

  | Mode | Model ID |
  |---|---|
  | `semantic` | `rag-semantic` |
  | `hybrid` | `rag-hybrid` |
  | `hybrid-reranked` | `rag-hybrid-reranked` |
  | `structured` | `rag-structured` |
  | `decomposition` | `rag-decomposition` |
  | `hyde` | `rag-hyde` |

  One shared registry. Each mode returns an honest `not_implemented` placeholder until its own story adds behavior.
- Derived corpus files: `data/processed/bns_sections.jsonl`, `data/processed/ipc_sections.jsonl`.
- Code lives in `src/building_with_rag/`, tests in `tests/`.

## Endpoints

- `GET /healthz`: safe status only. No secrets, no config values, no database call.
- `POST /v1/query`: `QueryRequest` in, `QueryResult` out. Owns the diagnostics.
- `GET /v1/models`: the six model IDs, OpenAI model-list format.
- `POST /v1/chat/completions`: text-only `ChatCompletionRequest`. Maps the model to the same `QueryRequest` and the same `run_pattern` path as `/v1/query`. The server sets `caller_id` (`WEBUI_DEMO_CALLER_ID`) and `generate_answer`. Supports JSON and standard SSE (role, content, stop, `[DONE]`), plus the OpenAI-style error envelope before streaming.

Open WebUI receives only normal answer text derived from the same `QueryResult`.

## Contracts

Defined once in the project and extended additively, never replaced: `QueryRequest`, `SemanticFilters`, `QueryResult`, `RetrievedChunk`, `GenerationResult`, `SubquestionEvidence`, `StructuredSignals`, `ChatCompletionRequest`, and a MongoDB-schema module. No parallel top-level API fields such as `outcome`, `evidence`, `answer`, `confidence`, `citations`, or `diagnostics`. The full `GenerationResult` stays in `QueryResult.generation`.

## Configuration

Settings come from environment variables via Pydantic settings. `.env` is untracked and holds secrets. `.env.example` is the canonical list of names. The app starts with no database or model credentials.

## Status

Draft for instructor approval. No seed files, dependencies, or code exist yet.
