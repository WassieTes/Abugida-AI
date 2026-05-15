import faiss
import numpy as np
import os
import pickle

# Dimension for all-MiniLM-L6-v2 embeddings
DIMENSION = 384

index = faiss.IndexFlatL2(DIMENSION)

# Store structured chunks instead of raw strings
stored_chunks = []  # [{"text": ..., "doc": ...}]


def add_embeddings(embeddings, chunks, doc_name="unknown"):
    global stored_chunks

    embeddings = np.array(embeddings).astype("float32")

    # IMPORTANT: normalize for better similarity behavior
    faiss.normalize_L2(embeddings)

    index.add(embeddings)

    for chunk in chunks:
        stored_chunks.append({
            "text": chunk,
            "doc": doc_name
        })


def search(query_embedding, k=3):
    query_embedding = np.array([query_embedding]).astype("float32")
    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(query_embedding, k)

    results = []

    for idx in indices[0]:
        if 0 <= idx < len(stored_chunks):
            results.append(stored_chunks[idx]["text"])

    return results


# ---------------- OPTIONAL PERSISTENCE ----------------

def save_store(path="storage/vector_store.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    faiss.write_index(index, path + ".faiss")

    with open(path, "wb") as f:
        pickle.dump(stored_chunks, f)


def load_store(path="storage/vector_store.pkl"):
    global index, stored_chunks

    if os.path.exists(path + ".faiss"):
        index = faiss.read_index(path + ".faiss")

    if os.path.exists(path):
        with open(path, "rb") as f:
            stored_chunks = pickle.load(f)