import re

def chunk_text(text, chunk_size=800, overlap=150):
    """
    Better chunking:
    - sentence-aware
    - overlap for context continuity
    """

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding sentence exceeds limit, store chunk
        if len(current_chunk) + len(sentence) > chunk_size:
            chunks.append(current_chunk.strip())

            # overlap handling (keep last part)
            current_chunk = current_chunk[-overlap:] + " " + sentence
        else:
            current_chunk += " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks