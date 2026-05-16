from rag.embedder import embed_query
from rag.vector_store import search


def retrieve_context(question, k=5):
    query_embedding = embed_query(question)

    results = search(query_embedding, k=k)

    # remove duplicates safely
    seen = set()
    filtered = []

    for r in results:
        if r not in seen:
            filtered.append(r)
            seen.add(r)

# fallback protection 
    if not filtered: 
      return "No relevant context found in document."

    return "\n\n".join(filtered)