import re
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.config import settings
from app.services.embeddings import embed_texts


def _get_client():
    return chromadb.PersistentClient(
        path=str(settings.chroma_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def get_document_count() -> int:
    """Get the number of documents (distinct files) in the collection."""
    try:
        collection = _get_collection()
        data = collection.get(include=["metadatas"])
        return len({m["document_id"] for m in data["metadatas"]})
    except Exception:
        return 0


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    # .txt, .md, .csv and other plain-text formats
    return path.read_text(encoding="utf-8", errors="ignore")


def _chunk_text(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    size = settings.chunk_size
    step = max(1, size - settings.chunk_overlap)
    return [text[i : i + size] for i in range(0, len(text), step)]


def index_document(filename: str, path: Path) -> dict:
    """Extract, chunk, embed and store a document. Returns DocumentInfo dict."""
    text = _extract_text(path)
    chunks = _chunk_text(text)
    if not chunks:
        raise ValueError("No extractable text found in the document.")

    document_id = str(uuid.uuid4())
    embeddings = embed_texts(chunks)
    ids = [f"{document_id}:{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    collection = _get_collection()
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {
        "id": document_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "status": "indexed",
    }


def list_documents() -> list[dict]:
    """Return one DocumentInfo dict per indexed file."""
    collection = _get_collection()
    data = collection.get(include=["metadatas"])
    docs: dict[str, dict] = {}
    for md in data["metadatas"]:
        did = md["document_id"]
        if did not in docs:
            docs[did] = {
                "id": did,
                "filename": md["filename"],
                "chunk_count": 0,
                "status": "indexed",
            }
        docs[did]["chunk_count"] += 1
    return list(docs.values())


def delete_document(document_id: str) -> bool:
    """Delete all chunks for a document. Returns True if anything was deleted."""
    collection = _get_collection()
    existing = collection.get(where={"document_id": document_id})
    if not existing["ids"]:
        return False
    collection.delete(where={"document_id": document_id})
    return True


def retrieve_context(
    question: str, document_ids: list[str] | None = None
) -> list[dict]:
    """Return the top-k relevant chunks as SourceChunk dicts."""
    collection = _get_collection()
    query_embedding = embed_texts([question])

    where = {"document_id": {"$in": document_ids}} if document_ids else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=settings.top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    sources: list[dict] = []
    for text, md, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        sources.append(
            {
                "document_id": md["document_id"],
                "filename": md["filename"],
                "text": text,
                "score": round(1 - dist, 4),  # cosine distance -> similarity
            }
        )
    return sources
