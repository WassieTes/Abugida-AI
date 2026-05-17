import faiss
import numpy as np
import os
import pickle

# ---------------- CONFIG ----------------

DIMENSION = 384

INDEX_PATH = "storage/faiss.index"
META_PATH = "storage/chunks.pkl"

# ---------------- CORE STORAGE ----------------

index = faiss.IndexFlatIP(DIMENSION)

# IMPORTANT:
# each entry index MUST match FAISS vector index
chunks_meta = []


# =========================================================
# ADD EMBEDDINGS
# =========================================================

def add_embeddings(
    embeddings,
    chunks,
    doc_name="unknown",
    doc_id=None
):

    global chunks_meta

    embeddings = np.array(embeddings).astype("float32")

    # normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    index.add(embeddings)

    for chunk in chunks:

        chunks_meta.append({
            "text": chunk,
            "doc_name": doc_name,
            "doc_id": doc_id
        })


# =========================================================
# SEARCH
# =========================================================

def search(
    query_embedding,
    k=3,
    doc_id=None,
    score_threshold=0.45
):

    query_embedding = np.array(
        [query_embedding]
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        k * 5
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0:
            continue

        if idx >= len(chunks_meta):
            continue

        # ignore weak similarity
        if float(score) < score_threshold:
            continue

        meta = chunks_meta[idx]

        # document isolation
        if doc_id is not None:

            if meta.get("doc_id") != doc_id:
                continue

        results.append({
            "text": meta["text"],
            "score": float(score)
        })

        if len(results) >= k:
            break

    return results


# =========================================================
# DELETE DOCUMENT (SAFE REBUILD VERSION)
# =========================================================

def remove_document_embeddings(doc_id):

    global index
    global chunks_meta

    new_vectors = []
    new_meta = []

    # rebuild everything safely
    for i in range(len(chunks_meta)):

        meta = chunks_meta[i]

        if meta.get("doc_id") == doc_id:
            continue

        # reconstruct vector safely
        vec = index.reconstruct(i)

        new_vectors.append(vec)
        new_meta.append(meta)

    # rebuild index
    new_index = faiss.IndexFlatIP(DIMENSION)

    if new_vectors:

        vectors_np = np.array(
            new_vectors
        ).astype("float32")

        faiss.normalize_L2(vectors_np)

        new_index.add(vectors_np)

    index = new_index
    chunks_meta = new_meta

    save_store()


# =========================================================
# GET DOCUMENT CHUNKS
# =========================================================

def get_document_chunks(doc_id):

    return [
        c for c in chunks_meta
        if c.get("doc_id") == doc_id
    ]


# =========================================================
# SAVE STORE
# =========================================================

def save_store():

    os.makedirs("storage", exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(chunks_meta, f)


# =========================================================
# LOAD STORE
# =========================================================

def load_store():

    global index, chunks_meta

    if os.path.exists(INDEX_PATH):

        index = faiss.read_index(INDEX_PATH)

    if os.path.exists(META_PATH):

        with open(META_PATH, "rb") as f:

            chunks_meta = pickle.load(f)