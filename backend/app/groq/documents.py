from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import DocumentInfo, UploadResponse
from app.services import rag

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".csv"}


@router.get("", response_model=list[DocumentInfo])
async def list_documents():
    return rag.list_documents()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    safe_name = Path(file.filename).name
    dest = settings.uploads_dir / safe_name

    content = await file.read()
    dest.write_bytes(content)

    try:
        doc = rag.index_document(safe_name, dest)
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to index document: {exc}"
        ) from exc

    return UploadResponse(
        message="Document uploaded and indexed successfully.",
        document=DocumentInfo(**doc),
    )


@router.delete("/{document_id}")
async def remove_document(document_id: str):
    deleted = rag.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted.", "document_id": document_id}
