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

UPLOAD_FOLDER = "storage/documents"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # ---------------- VALIDATE PDF ----------------

    if not file.filename.endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF allowed"
        )

    file_bytes = await file.read()

    file_hash = get_file_hash(file_bytes)

    # ---------------- DUPLICATE DETECTION ----------------

    existing = db.query(Document)\
        .filter(
            Document.file_hash == file_hash
        ).first()

    if existing:

        return {
            "success": False,
            "message": "Duplicate document already exists"
        }

    # ---------------- CREATE CHAT ----------------

    new_chat = Chat(
        title=file.filename[:40]
    )

    db.add(new_chat)

    db.commit()

    db.refresh(new_chat)

    # ---------------- SAVE FILE ----------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as f:

        f.write(file_bytes)

    # ---------------- CREATE DOCUMENT ----------------

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

    # ---------------- READ PDF ----------------

    pdf = fitz.open(file_path)

    text = ""

    for page in pdf:

        text += (
            page.get_text() or ""
        ) + "\n"

    if not text.strip():

        raise HTTPException(
            status_code=400,
            detail="No readable text found"
        )

    # ---------------- CHUNK ----------------

    chunks = chunk_text(text)

    embeddings = generate_embeddings(chunks)

    # ---------------- SAVE EMBEDDINGS ----------------

    add_embeddings(
        embeddings,
        chunks,
        doc_name=file.filename,
        doc_id=document.id
    )

    save_store()

    # ---------------- UPDATE DOCUMENT ----------------

    document.chunk_count = len(chunks)

    document.status = "active"

    db.commit()

    # ---------------- RESPONSE ----------------

    return {
        "success": True,
        "chat_id": new_chat.id,
        "document_id": document.id,
        "file": file.filename,
        "chunks": len(chunks)
    }