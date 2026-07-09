from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    status: str


class UploadResponse(BaseModel):
    message: str
    document: DocumentInfo


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[str] | None = None


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    model: str


class HealthResponse(BaseModel):
    status: str
    documents_indexed: int
    model: str
