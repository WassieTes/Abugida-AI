import re

def chunk_text(text, chunk_size=500, overlap=80):
    """
    Better than character slicing: sentence-aware + overlap context
    """

    sentences = re.split(r'(?<=[.!?])\s+', text) 
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
          current += " " + sentence

        else:
          chunks.append(current.strip())
          current = current[-overlap:] + " " + sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks