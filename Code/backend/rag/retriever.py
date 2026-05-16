from rag.embedder import embed_query

from rag.vector_store import search


def retrieve_context(
    question,
    k=3,
    doc_id=None
):

    query_embedding = embed_query(question)

    results = search(
        query_embedding,
        k=k,
        doc_id=doc_id
    )

    seen = set()

    filtered = []

    for r in results:

        if r not in seen:

            filtered.append(r)

            seen.add(r)

    if not filtered:

        return ""

    return "\n\n".join(filtered)