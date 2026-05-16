import faiss
import numpy as np
import os
import pickle

DIMENSION = 384

INDEX_PATH = "storage/faiss.index"

META_PATH = "storage/chunks.pkl"


index = faiss.IndexFlatIP(DIMENSION)

chunks_meta = []


# ---------------- ADD EMBEDDINGS ----------------

def add_embeddings(
    embeddings,
    chunks,
    doc_name="unknown",
    doc_id=None
):

    global chunks_meta

    embeddings = np.array(
        embeddings
    ).astype("float32")

    faiss.normalize_L2(embeddings)

    index.add(embeddings)

    for chunk in chunks:

        chunks_meta.append({
            "text": chunk,
            "doc": doc_name,
            "doc_id": doc_id
        })


# ---------------- SEARCH ----------------

def search(
    query_embedding,
    k=5,
    doc_id=None
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

    for idx in indices[0]:

        if idx < 0:
            continue

        if idx >= len(chunks_meta):
            continue

        meta = chunks_meta[idx]

        # document filtering
        if doc_id is not None:

            if meta["doc_id"] != doc_id:
                continue

        results.append(meta["text"])

        if len(results) >= k:
            break

    return results


# ---------------- REMOVE DOCUMENT ----------------

def remove_document_embeddings(doc_id):

    global index
    global chunks_meta

    remaining_meta = []

    remaining_vectors = []

    for i, meta in enumerate(chunks_meta):

        if meta["doc_id"] != doc_id:

            remaining_meta.append(meta)

            vec = index.reconstruct(i)

            remaining_vectors.append(vec)

    # rebuild fresh index
    new_index = faiss.IndexFlatIP(DIMENSION)

    if remaining_vectors:

        vectors_np = np.array(
            remaining_vectors
        ).astype("float32")

        new_index.add(vectors_np)

    index = new_index

    chunks_meta = remaining_meta

    save_store()


# ---------------- GET DOCUMENT CHUNKS ----------------

def get_document_chunks(doc_id):

    return [
        c for c in chunks_meta
        if c["doc_id"] == doc_id
    ]


# ---------------- SAVE ----------------

def save_store():

    os.makedirs("storage", exist_ok=True)

    faiss.write_index(
        index,
        INDEX_PATH
    )

    with open(META_PATH, "wb") as f:

        pickle.dump(chunks_meta, f)


# ---------------- LOAD ----------------

def load_store():

    global index
    global chunks_meta

    if os.path.exists(INDEX_PATH):

        index = faiss.read_index(
            INDEX_PATH
        )

    if os.path.exists(META_PATH):

        with open(META_PATH, "rb") as f:

            chunks_meta = pickle.load(f)