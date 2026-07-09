from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import HealthResponse
from app.groq import chat, documents
from app.services import rag

app = FastAPI(
    title="RAG Eval Chatbot API",
    description="Upload documents and ask questions using RAG + an OpenAI-compatible LLM API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        documents_indexed=rag.get_document_count(),
        model=settings.llm_model,
    )
