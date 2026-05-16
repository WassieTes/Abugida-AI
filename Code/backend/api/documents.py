from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database.db import get_db

from database.models import Document

from rag.vector_store import (
    remove_document_embeddings,
    get_document_chunks
)

router = APIRouter()


# ---------------- LIST DOCUMENTS ----------------

@router.get("/documents/{chat_id}")
def list_documents(
    chat_id: int,
    db: Session = Depends(get_db)
):

    documents = db.query(Document)\
        .filter(
            Document.chat_id == chat_id,
            Document.status != "deleted"
        ).all()

    return {
        "success": True,
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "chunk_count": d.chunk_count,
                "status": d.status,
                "created_at": d.created_at
            }
            for d in documents
        ]
    }


# ---------------- DELETE DOCUMENT ----------------

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(Document)\
        .filter(Document.id == doc_id)\
        .first()

    if not document:

        return {
            "success": False,
            "error": "Document not found"
        }

    # remove vectors
    remove_document_embeddings(doc_id)

    # soft delete
    document.status = "deleted"

    db.commit()

    return {
        "success": True
    }


# ---------------- INSPECT CHUNKS ----------------

@router.get("/documents/{doc_id}/chunks")
def inspect_chunks(doc_id: int):

    chunks = get_document_chunks(doc_id)

    return {
        "success": True,
        "chunks": chunks
    }