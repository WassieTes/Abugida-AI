from sentence_transformers import SentenceTransformer
import numpy as np

# Better upgrade option later: "BAAI/bge-small-en-v1.5"
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks):
    embeddings = model.encode(
        chunks,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return embeddings.astype(np.float32)


def embed_query(text):
    embedding = model.encode(
        [text],
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return embedding[0].astype(np.float32)