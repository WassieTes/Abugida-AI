from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks):
    return model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype("float32")


def embed_query(text):
    return model.encode(
        [text],
        convert_to_numpy=True,
        show_progress_bar=False
    )[0].astype("float32")