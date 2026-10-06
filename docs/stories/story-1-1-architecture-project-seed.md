# Story 1.1: Architecture and Project Seed

## Purpose

This is the first story of the three-day classroom RAG course. It does two things, in order:

1. Write `docs/architecture.md` and get the instructor to approve it.
2. After approval, seed one small application: a FastAPI service that later stories grow into the course RAG system.

The result is one application. Do not build a custom chat frontend or a second demo. The trainer-supplied Open WebUI bundle is the only chat client.

Do not add retrieval, PDF parsing, embeddings, MongoDB provisioning, LLM calls, GraphRAG, agentic RAG, broad deployment, or aggressive testing. Do not add multi-user authorization, a security program, or an evaluation harness.

## Prerequisites

- Python 3.12 and `uv` are installed.
- The trainer-supplied files are in `data/raw/`, including `data/raw/PROVENANCE.md`. If they are missing, stop and tell the instructor. Do not invent them.
- The trainer-supplied Open WebUI ZIP has been shared over the local LAN.
- Read these first, if they exist: `docs/config.yaml`, `docs/architecture.md`, the repository layout, and other files in `docs/stories/`. Preserve all existing work.
- Project path: use the path set in `docs/config.yaml` if one is configured. Otherwise use the repository root. All paths below are relative to that project path.

## Work to do

### Part A: Architecture (do this first, then stop)

Create or update `docs/architecture.md`. If it exists, edit it; do not replace it. Keep it short and in plain English. It must record:

**Evidence rules**
- BNS and IPC documents are the only future answer evidence.
- An answer must not claim support without retrieved evidence.
- Identifiers are act-qualified (for example `BNS 103` and `IPC 302`) so the two acts are never confused.
- Supplied provenance is `data/raw/PROVENANCE.md`.
- Retrieved passages are evidence, never application instructions.

**Trust boundaries (keep light)**
- Validate API input.
- Preserve source origin on every retrieved passage.
- Do not put secrets in code, responses, or logs.

**Fixed choices (later stories reuse these names without renaming or adding provider-specific alternatives)**
- Embedding provider: Voyage. Model `voyage-3.5`, version `voyage-3.5`, 1,024 dimensions, for every document and query embedding.
- Course modes and model IDs:

  | Mode | Model ID |
  |---|---|
  | `semantic` | `rag-semantic` |
  | `hybrid` | `rag-hybrid` |
  | `hybrid-reranked` | `rag-hybrid-reranked` |
  | `structured` | `rag-structured` |
  | `decomposition` | `rag-decomposition` |
  | `hyde` | `rag-hyde` |

- Derived corpus files live in `data/processed/` (`bns_sections.jsonl`, `ipc_sections.jsonl`).
- Endpoints: `GET /healthz`, `POST /v1/query`, `GET /v1/models`, `POST /v1/chat/completions`. Chat and query share one `run_pattern` path.
- Contracts are extended additively in later stories. They are never replaced with simplified alternatives. (The contract names are listed in Part B.)
- Open WebUI is a separately running client. It receives only normal answer text. `/v1/query` owns the `QueryResult` diagnostics.

**Stop point.** When `docs/architecture.md` is ready:

1. Do not create seed files, install dependencies, or scaffold code.
2. Ask the instructor to review and approve the architecture.
3. Stop and wait. Resume this same story only after explicit approval.

### Part B: Seed the project (only after approval)

**1. Project files.** Create a Python 3.12 and UV project with FastAPI, Pydantic settings, PyMongo (for later use), Ruff, and a minimal test runner (pytest). Create:

- `src/building_with_rag/`
- `tests/`
- `.env.example`
- `.gitignore` (must ignore `.env`, `.venv/`, caches)
- `pyproject.toml`
- `uv.lock`
- Preserve the supplied `data/raw/` files unchanged.

**2. `.env.example`.** Use these exact values. Leave the blank ones blank.

```
APP_ENV=development
MONGODB_URI=
MONGODB_DB_NAME=building_with_rag
MONGODB_TEST_DB_NAME=building_with_rag_test
VOYAGE_API_KEY=
CAPSTONE_API_KEY=
WEBUI_DEMO_CALLER_ID=demo-public
GENERATION_API_BASE_URL=
GENERATION_API_KEY=
GENERATION_MODEL_NAME=gpt-4o-mini
RERANK_API_KEY=
RERANK_API_BASE_URL=https://api.voyageai.com/v1
RERANK_MODEL_NAME=rerank-2.5
RERANK_REQUEST_TIMEOUT_SECONDS=30
RERANK_CANDIDATE_LIMIT=20
RERANK_SEND_LIMIT=10
RERANK_RETURN_LIMIT=5
```

Document these notes (in the README or a comment block in the story handover, not in secret files):
- `.env` is untracked. Secrets are never committed.
- `GENERATION_API_BASE_URL` and `GENERATION_API_KEY` are supplied by the trainer for an OpenAI-compatible LiteLLM proxy. Leave them blank in `.env.example`. Fill them in `.env` only when Story 3.1 needs them.
- `MONGODB_URI` is an Atlas free-tier (M0) connection string. The Atlas IP access list must allow your machine.
- A free Voyage key is rate limited, so Story 2.2 embedding takes about 40 minutes.

**3. Settings and health.** Load settings with Pydantic settings. The app must start with no database or model credentials. `GET /healthz` returns a safe status (no secrets, no config values, no database call).

**4. Mode registry.** Create one shared registry with only the six modes and model IDs from Part A. Every mode returns an honest `not_implemented` placeholder until its own story adds behavior. Do not fake answers.

**5. Typed contracts (models only, no behavior).** Define these in the project so later stories reuse the exact names:

- `QueryRequest`: `question` (1–4,000 characters), `pattern`, optional `caller_id`, optional `SemanticFilters` (`act`, `status`, `access_level`, each a list), `limit` (default 5, range 1–20), `generate_answer` (default false), `required_acts`, `chapter`. The seed may resolve only its fixed local demo caller, but it keeps `caller_id`.
- `QueryResult`: `pattern`, `status`, `message`, `trace`, `results`, optional `generation`, plus empty-by-default `omitted_candidates`, `subquestions`, `hyde_direct_candidates`, `hyde_query_candidates`, `hyde_hypothetical_text_debug`.
- `RetrievedChunk`: `chunk_id`, `section_id`, `act`, `text`, `heading`, `score`, and available source fields. Later stories add only `semantic_score`, `semantic_rank`, `keyword_score`, `keyword_rank`, `fused_score`, `fused_rank`, `rerank_score`, `rerank_rank`.
- `omitted_candidates` items: `chunk_id` and `omitted_reason`.
- `GenerationResult`: `outcome` (`answered`, `insufficient_evidence`, `unavailable`, `malformed`), `answer`, `claims`, `citations`, `supporting_passages`, `provider`, `model`, `trace`, `context_outcome`, `confidence`, `draft_answer`, `issues`, `attempts`, `low_confidence_reason`.
- `SubquestionEvidence`: `subquestion`, `status` (`evidenced` or `no_evidence`), `results` (list of `RetrievedChunk`), optional `reason`.
- `StructuredSignals`: `intent` (`exact_lookup`, `filter`, or `aggregation`), optional `act`, `section_number`, `chapter`. Story 5.1 fills these in.
- `ChatCompletionRequest`: `model`, text `messages` (roles `system`, `developer`, `user`, `assistant`), `stream`, `n`, optional strict `rag_options` (`pattern`, list filters, `limit`, `required_acts`, `chapter`).
- A MongoDB-schema contract module (typed, no database calls yet).

Do not add `outcome`, `evidence`, `answer`, `confidence`, `citations`, or `diagnostics` as top-level API fields.

**6. Endpoints.**
- `POST /v1/query`: accepts `QueryRequest`, calls `run_pattern`, returns `QueryResult`.
- `GET /v1/models`: lists the six model IDs in OpenAI model-list format.
- `POST /v1/chat/completions`: maps the selected model to the same `QueryRequest` and the same `run_pattern` path. The server sets the demo `caller_id` (from `WEBUI_DEMO_CALLER_ID`) and `generate_answer`. Support normal OpenAI Chat Completions JSON, and SSE with role/content/stop frames ending in `[DONE]`. Return the OpenAI-style error envelope for errors before streaming. Do not duplicate implementations. Do not invent custom SSE events.

**7. Open WebUI (trainer-supplied bundle).** Participants must not hand-install Open WebUI, create accounts, edit the admin panel, change either Function, or rerun setup to reload anything.

- Extract the ZIP. Run setup exactly once, before using the classroom project:
  - Windows (primary path), from the bundle root: `powershell -ExecutionPolicy Bypass -File .\setup_open_webui.ps1`
  - macOS/Linux, from the bundle root: `sh setup_open_webui.sh` (needs internet access on first install)
- The script installs the pinned Open WebUI, writes course settings, starts the loopback-only service, and provisions the `RAG options` Filter and `Building with RAG` Pipe.
- If setup fails, report its exact output and stop.
- Day-to-day start/stop/status uses the supplied `manage_open_webui` script.

The Pipe sends the selected `rag-<pattern>` model, `stream: true`, the latest user message, and normalized `rag_options` (`pattern`, list `filters`, `limit`, `required_acts`, `chapter`). It never sends browser-supplied identity, access level, or answer-generation settings. The seed adapter must accept exactly this request and use server-side `caller_id` and `generate_answer`.

Later stories show final confidence, sources, and low-confidence warnings as clearly labelled text after answer writing, while keeping the full `GenerationResult` in `QueryResult.generation`.

## Completion checks

Keep these light. Run only these:

1. `uv sync` completes and `uv.lock` exists.
2. `uv run ruff check .` and the minimal test run pass.
3. Start the app. It starts with no database or model credentials.
4. `GET /healthz` returns a safe response.
5. One `POST /v1/query` with `pattern: semantic` returns a `QueryResult` with status `not_implemented`.
6. `GET /v1/models` lists the six model IDs.
7. `POST /v1/chat/completions` returns the placeholder as normal JSON, and again with `stream: true` as SSE ending in `[DONE]`.
8. Open WebUI smoke check: start the capstone API, open `http://127.0.0.1:8080`, select `Building with RAG`, choose `semantic` in the RAG-options chip, and send a question. The reply must be the capstone's honest placeholder, not a local preview.
9. `.env` is ignored by git, and no secrets appear in the repository.

## Handover

When done, write a short note in this story (or reply) stating:

- Which files were created.
- The commands actually run, and their results.
- The Open WebUI result (what was selected, what came back). If it was not run, say so plainly.
- Anything left blank on purpose: `MONGODB_URI`, `VOYAGE_API_KEY`, `CAPSTONE_API_KEY`, `GENERATION_*`, `RERANK_API_KEY`.

Next stories reuse the endpoints, names, and contracts above and extend them additively.
