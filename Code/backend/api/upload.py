from fastapi import APIRouter, UploadFile, File
import fitz
import os

from rag.chunker import chunk_text
from rag.embedder import generate_embeddings
from rag.vector_store import add_embeddings

router = APIRouter()

UPLOAD_FOLDER = "storage/documents"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:
        text += page.get_text()

    chunks = chunk_text(text)

    embeddings = generate_embeddings(chunks)

    add_embeddings(embeddings, chunks)

    return {
        "message": "PDF processed successfully",
        "chunks": len(chunks)
    }