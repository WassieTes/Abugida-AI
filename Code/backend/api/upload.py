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
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    pdf = fitz.open(file_path)

    text = ""
    for page in pdf:
        text += (page.get_text() or "") + "\n"

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found")

    chunks = chunk_text(text)
    embeddings = generate_embeddings(chunks)

    add_embeddings(embeddings, chunks, doc_name=file.filename)
    save_store()

    return {
        "success": True,
        "file": file.filename,
        "chunks": len(chunks)
    }