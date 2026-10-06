from building_with_rag.contracts import QueryRequest, QueryResult


def run_pattern(request: QueryRequest) -> QueryResult:
    """Single shared path for /v1/query and /v1/chat/completions."""
    return QueryResult(
        pattern=request.pattern,
        status="not_implemented",
        message=f"Pattern '{request.pattern}' is not implemented yet.",
        trace=["seed:placeholder"],
    )
