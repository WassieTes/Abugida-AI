from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz
import os

from rag.chunker import chunk_text
from rag.embedder import generate_embeddings
from rag.vector_store import add_embeddings, save_store

router = APIRouter()

UPLOAD_FOLDER = "storage/documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text safely
    try:
        pdf = fitz.open(file_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to open PDF")

    text = ""

    for page in pdf:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise HTTPException(status_code=400, detail="PDF has no readable text")

    # Chunking
    chunks = chunk_text(text)

    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks created from PDF")

    # Embeddings
    embeddings = generate_embeddings(chunks)

    # Store into vector DB (IMPORTANT: include doc name)
    add_embeddings(embeddings, chunks, doc_name=file.filename)

    # SAVE PERSISTENT STATE (critical fix)
    save_store()

    return {
        "message": "PDF processed successfully",
        "file": file.filename,
        "chunks": len(chunks)
    }