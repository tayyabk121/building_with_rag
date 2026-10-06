import json
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse

from building_with_rag.contracts import (
    ChatCompletionRequest,
    QueryRequest,
    QueryResult,
)
from building_with_rag.registry import MODEL_TO_MODE, MODES
from building_with_rag.service import run_pattern
from building_with_rag.settings import get_settings

app = FastAPI(title="Building with RAG")


def _error(status: int, message: str, err_type: str, param: str | None = None):
    return JSONResponse(
        status_code=status,
        content={
            "error": {"message": message, "type": err_type, "param": param, "code": None}
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    if request.url.path == "/v1/chat/completions":
        return _error(400, "Invalid request body.", "invalid_request_error")
    return JSONResponse(status_code=422, content={"detail": "Invalid request."})


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/v1/query", response_model=QueryResult)
def query(request: QueryRequest) -> QueryResult:
    return run_pattern(request)


@app.get("/v1/models")
def models():
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "created": 0, "owned_by": "building-with-rag"}
            for m in MODES.values()
        ],
    }


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    mode = MODEL_TO_MODE.get(req.model)
    if mode is None:
        return _error(404, f"Model '{req.model}' not found.", "invalid_request_error", "model")
    user_texts = [m.content for m in req.messages if m.role == "user"]
    if not user_texts or not user_texts[-1].strip():
        return _error(400, "A non-empty user message is required.", "invalid_request_error", "messages")

    opts = req.rag_options
    if opts and opts.pattern and opts.pattern != mode:
        return _error(400, "rag_options.pattern does not match model.", "invalid_request_error", "rag_options")
    fields: dict = {}
    if opts:
        if opts.filters is not None:
            fields["filters"] = opts.filters
        if opts.limit is not None:
            fields["limit"] = opts.limit
        if opts.required_acts is not None:
            fields["required_acts"] = opts.required_acts
        if opts.chapter is not None:
            fields["chapter"] = opts.chapter
    try:
        qreq = QueryRequest(
            question=user_texts[-1],
            pattern=mode,
            caller_id=get_settings().webui_demo_caller_id,
            generate_answer=False,
            **fields,
        )
    except ValueError:
        return _error(400, "Invalid question.", "invalid_request_error", "messages")

    text = run_pattern(qreq).message
    cid = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    if not req.stream:
        return {
            "id": cid,
            "object": "chat.completion",
            "created": created,
            "model": req.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def frame(delta: dict, finish: str | None) -> str:
        return _sse(
            {
                "id": cid,
                "object": "chat.completion.chunk",
                "created": created,
                "model": req.model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            }
        )

    def stream():
        yield frame({"role": "assistant"}, None)
        yield frame({"content": text}, None)
        yield frame({}, "stop")
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
