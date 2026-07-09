from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services import rag
from app.services.llm import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if rag.get_document_count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed. Upload a document first.",
        )

    sources = rag.retrieve_context(request.question, request.document_ids)
    if not sources:
        raise HTTPException(
            status_code=404,
            detail="No relevant context found for your question.",
        )

    context = "\n\n---\n\n".join(
        f"[{s['filename']}] {s['text']}" for s in sources
    )

    try:
        answer = await generate_answer(request.question, context)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {exc}",
        ) from exc

    return ChatResponse(
        answer=answer,
        sources=[SourceChunk(**s) for s in sources],
        model=settings.llm_model,
    )
