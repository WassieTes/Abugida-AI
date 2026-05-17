from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

import fitz
import os

from rag.chunker import chunk_text
from rag.embedder import generate_embeddings

from rag.vector_store import (
    add_embeddings,
    save_store
)

from rag.file_utils import get_file_hash

from database.db import get_db

from database.models import (
    Document,
    Chat
)

router = APIRouter()

# =====================================================
# STORAGE FOLDERS
# =====================================================

BASE_STORAGE = "storage"

DOCUMENT_FOLDER = os.path.join(
    BASE_STORAGE,
    "documents"
)

os.makedirs(
    DOCUMENT_FOLDER,
    exist_ok=True
)


# =====================================================
# UPLOAD PDF
# =====================================================

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # =====================================================
    # VALIDATE PDF
    # =====================================================

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    # =====================================================
    # READ FILE
    # =====================================================

    file_bytes = await file.read()

    file_hash = get_file_hash(file_bytes)

    # =====================================================
    # CHECK EXISTING DOCUMENT
    # =====================================================

    existing = db.query(Document).filter(
        Document.file_hash == file_hash
    ).first()

    # =====================================================
    # REUSE EXISTING DOCUMENT
    # =====================================================

    if existing:

        new_chat = Chat(
            title=existing.filename[:40]
        )

        db.add(new_chat)

        db.commit()

        db.refresh(new_chat)

        return {
            "success": True,
            "message": "Existing document reused",
            "chat_id": new_chat.id,
            "document_id": existing.id,
            "file": existing.filename,
            "chunks": existing.chunk_count,
            "reused": True
        }

    # =====================================================
    # CREATE CHAT
    # =====================================================

    new_chat = Chat(
        title=file.filename[:40]
    )

    db.add(new_chat)

    db.commit()

    db.refresh(new_chat)

    # =====================================================
    # SAVE FILE
    # =====================================================

    safe_filename = f"{file_hash}.pdf"

    file_path = os.path.join(
        DOCUMENT_FOLDER,
        safe_filename
    )

    with open(file_path, "wb") as f:

        f.write(file_bytes)

    # =====================================================
    # CREATE DOCUMENT RECORD
    # =====================================================

    document = Document(
        chat_id=new_chat.id,
        filename=file.filename,
        path=file_path,
        file_hash=file_hash,
        status="processing"
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    # =====================================================
    # EXTRACT PDF TEXT
    # =====================================================

    try:

        pdf = fitz.open(file_path)

        text = ""

        for page in pdf:

            text += (
                page.get_text() or ""
            ) + "\n"

        pdf.close()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF reading failed: {str(e)}"
        )

    # =====================================================
    # VALIDATE TEXT
    # =====================================================

    if not text.strip():

        raise HTTPException(
            status_code=400,
            detail="No readable text found"
        )

    # =====================================================
    # CHUNK TEXT
    # =====================================================

    chunks = chunk_text(text)

    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="No chunks generated"
        )

    # =====================================================
    # GENERATE EMBEDDINGS
    # =====================================================

    embeddings = generate_embeddings(chunks)

    # =====================================================
    # SAVE EMBEDDINGS
    # =====================================================

    add_embeddings(
        embeddings=embeddings,
        chunks=chunks,
        doc_name=file.filename,
        doc_id=document.id
    )

    save_store()

    # =====================================================
    # UPDATE DOCUMENT
    # =====================================================

    document.chunk_count = len(chunks)

    document.status = "active"

    db.commit()

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success": True,
        "chat_id": new_chat.id,
        "document_id": document.id,
        "file": file.filename,
        "chunks": len(chunks),
        "stored_at": file_path
    }