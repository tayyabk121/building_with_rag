"""MongoDB schema contract (types only; no database calls)."""

from pydantic import BaseModel

EMBEDDING_PROVIDER = "voyage"
EMBEDDING_MODEL = "voyage-3.5"
EMBEDDING_MODEL_VERSION = "voyage-3.5"
EMBEDDING_DIMENSIONS = 1024

CHUNKS_COLLECTION = "chunks"


class ChunkDocument(BaseModel):
    chunk_id: str
    section_id: str
    act: str
    text: str
    heading: str | None = None
    source_file: str | None = None
    source_page: int | None = None
    embedding: list[float] | None = None
    embedding_model: str = EMBEDDING_MODEL
    embedding_model_version: str = EMBEDDING_MODEL_VERSION
