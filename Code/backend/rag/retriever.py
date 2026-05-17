from rag.embedder import embed_query

from rag.vector_store import search


def retrieve_context(
    question,
    document_id=None,
    k=3
):

    query_embedding = embed_query(question)

    results = search(
        query_embedding,
        k=k,
        doc_id=document_id,
        score_threshold=0.45
    )

    if not results:
        return ""

    unique_chunks = []

    seen = set()

    for item in results:

        text = item["text"]

        if text in seen:
            continue

        seen.add(text)

        unique_chunks.append(text)

    context = "\n\n".join(unique_chunks)

    # IMPORTANT:
    # keep prompt small for local model
    context = context[:2500]

    return context

def retrieve_document_overview(
    document_id,
    max_chunks=6
):

    from rag.vector_store import chunks_meta

    document_chunks = []

    for item in chunks_meta:

        if item.get("doc_id") == document_id:

            document_chunks.append(
                item["text"]
            )

        if len(document_chunks) >= max_chunks:
            break

    if not document_chunks:
        return ""

    context = "\n\n".join(document_chunks)

    return context[:4000]