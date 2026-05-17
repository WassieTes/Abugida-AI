from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from sqlalchemy.orm import Session

from database.db import get_db

from database.models import (
    Chat,
    Message,
    Document
)

from rag.retriever import retrieve_context

from llm.llama_engine import stream_llm

router = APIRouter()


class ChatRequest(BaseModel):

    question: str

    chat_id: int | None = None

    document_id: int | None = None


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # ================= VALIDATE DOCUMENT =================

    if request.document_id is None:

        def no_doc_stream():
            yield "Please upload a document first."

        return StreamingResponse(
            no_doc_stream(),
            media_type="text/plain"
        )

    document = db.query(Document).filter(
        Document.id == request.document_id
    ).first()

    if not document:

        def invalid_doc_stream():
            yield "Document not found."

        return StreamingResponse(
            invalid_doc_stream(),
            media_type="text/plain"
        )

    # ================= CREATE CHAT =================

    if request.chat_id is None:

        new_chat = Chat(
            title=request.question[:40]
        )

        db.add(new_chat)

        db.commit()

        db.refresh(new_chat)

        chat_id = new_chat.id

    else:

        chat_id = request.chat_id

    # ================= SAVE USER MESSAGE =================

    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.question
    )

    db.add(user_message)

    db.commit()

    # ================= RETRIEVE CONTEXT =================

    context = retrieve_context(
        question=request.question,
        document_id=request.document_id,
        k=5
    )

    # ================= NO CONTEXT =================

    if not context:

        answer = (
            "I cannot find relevant information "
            "in the uploaded document."
        )

        ai_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=answer
        )

        db.add(ai_message)

        db.commit()

        def empty_stream():
            yield answer

        return StreamingResponse(
            empty_stream(),
            media_type="text/plain"
        )

    # ================= PROMPT =================

    prompt = f"""
You are an offline AI tutor.

RULES:
- Use ONLY the provided context
- Do NOT hallucinate
- If answer does not exist in context say:
  "Not found in document"

Context:
{context}

Question:
{request.question}

Answer:
"""

    # ================= STREAMING =================

    def generate():

        full_answer = ""

        try:

            for token in stream_llm(request.question,context):

                full_answer += token

                yield token

            # SAVE AI MESSAGE
            ai_message = Message(
                chat_id=chat_id,
                role="assistant",
                content=full_answer
            )

            db.add(ai_message)

            db.commit()

        except Exception as e:

            error_message = f"\n\nLLM Error: {str(e)}"

            yield error_message

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )