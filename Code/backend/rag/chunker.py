import re


def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_paragraphs(text):

    paragraphs = text.split("\n")

    cleaned = []

    for p in paragraphs:

        p = clean_text(p)

        if len(p) > 40:
            cleaned.append(p)

    return cleaned


def chunk_text(
    text,
    chunk_size=700,
    overlap=120
):

    paragraphs = split_paragraphs(text)

    chunks = []

    current_chunk = ""

    for paragraph in paragraphs:

        # add paragraph safely
        if len(current_chunk) + len(paragraph) < chunk_size:

            current_chunk += "\n" + paragraph

        else:

            if current_chunk.strip():

                chunks.append(
                    current_chunk.strip()
                )

            # overlap keeps context continuity
            overlap_text = current_chunk[-overlap:]

            current_chunk = (
                overlap_text +
                "\n" +
                paragraph
            )

    if current_chunk.strip():

        chunks.append(
            current_chunk.strip()
        )

    return chunks