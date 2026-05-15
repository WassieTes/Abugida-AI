from rag.embedder import embed_query
from rag.vector_store import search


def retrieve_context(question, k=4):
    """
    Retrieves most relevant chunks from FAISS
    """

    query_embedding = embed_query(question)

    results = search(query_embedding, k=k)

    # Remove duplicates while preserving order
    seen = set()
    filtered = []

    for r in results:
        if r not in seen:
            filtered.append(r)
            seen.add(r)

    return "\n\n".join(filtered)