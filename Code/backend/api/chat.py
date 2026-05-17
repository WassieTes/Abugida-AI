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


# =====================================================
# REQUEST MODEL
# =====================================================

class ChatRequest(BaseModel):

    question: str

    chat_id: int | None = None

    document_id: int | None = None


# =====================================================
# CHAT ROUTE
# =====================================================

@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # =================================================
    # VALIDATE DOCUMENT
    # =================================================

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

    # =================================================
    # CREATE CHAT
    # =================================================

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

    # =================================================
    # SAVE USER MESSAGE
    # =================================================

    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.question
    )

    db.add(user_message)

    db.commit()

    # =================================================
    # RECENT CHAT HISTORY
    # =================================================

    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(
        Message.created_at.asc()
    ).all()

    # KEEP ONLY RECENT MEMORY
    messages = messages[-8:]

    # =================================================
    # RETRIEVE CONTEXT
    # =================================================

    context = retrieve_context(
        question=request.question,
        document_id=request.document_id,
        k=5
    )

    # LIMIT CONTEXT SIZE
    context = context[:2500]

    # =================================================
    # NO CONTEXT
    # =================================================

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

    # =================================================
    # STREAM GENERATION
    # =================================================

    def generate():

        full_answer = ""

        try:

            for token in stream_llm(
                question=request.question,
                context=context,
                history=messages
            ):

                full_answer += token

                yield token

            # SAVE AI RESPONSE
            ai_message = Message(
                chat_id=chat_id,
                role="assistant",
                content=full_answer
            )

            db.add(ai_message)

            db.commit()

        except Exception as e:

            yield f"\n\nLLM Error: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )