from rag.embedder import embed_query

from rag.vector_store import (
    search,
    chunks_meta
)


def retrieve_context(
    question,
    document_id=None,
    k=3
):

    query_embedding = embed_query(question)

    # IMPORTANT:
    # search already supports doc filtering
    results = search(
        query_embedding,
        k=k,
        doc_id=document_id
    )

    # remove duplicates safely
    filtered = []

    seen = set()

    for r in results:

        if r in seen:
            continue

        seen.add(r)

        filtered.append(r)

    if not filtered:
        return ""

    return "\n\n".join(filtered)