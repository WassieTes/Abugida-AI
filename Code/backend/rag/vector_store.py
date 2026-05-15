import faiss
import numpy as np
import os
import pickle

DIMENSION = 384  # for all-MiniLM-L6-v2

INDEX_PATH = "storage/faiss.index"
META_PATH = "storage/chunks.pkl"

index = faiss.IndexFlatIP(DIMENSION)  # cosine similarity (IMPORTANT FIX)

chunks_meta = []  # [{"text":..., "doc":..., "id":...}]


def add_embeddings(embeddings, chunks, doc_name="unknown"):
    global chunks_meta

    embeddings = np.array(embeddings).astype("float32")

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    index.add(embeddings)

    for i, chunk in enumerate(chunks):
        chunks_meta.append({
            "text": chunk,
            "doc": doc_name,
            "id": len(chunks_meta) + i
        })


def search(query_embedding, k=5):
    query_embedding = np.array([query_embedding]).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, k)

    results = []

    for idx in indices[0]:
        if 0 <= idx < len(chunks_meta):
            results.append(chunks_meta[idx]["text"])

    return results


# ---------------- PERSISTENCE ----------------

def save_store():
    os.makedirs("storage", exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(chunks_meta, f)


def load_store():
    global index, chunks_meta

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)

    if os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            chunks_meta = pickle.load(f)