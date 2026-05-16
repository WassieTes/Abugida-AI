from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from llm.llama_engine import ask_llm

from rag.retriever import retrieve_context

from database.db import get_db
from database.models import Chat, Message

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    chat_id: int | None = None


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # ---------------- CREATE CHAT ----------------

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

    # ---------------- SAVE USER MESSAGE ----------------

    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.question
    )

    db.add(user_message)
    db.commit()

    # ---------------- RETRIEVE CONTEXT ----------------

    context = retrieve_context(request.question)

    if not context:

        answer = "I cannot find relevant information in the uploaded documents."

    else:

        prompt = f"""
You are an offline AI tutor.

RULES:
- Use ONLY the context
- If not found, say "Not found in document"

Context:
{context}

Question:
{request.question}

Answer:
"""

        try:
            answer = ask_llm(prompt)

        except Exception as e:

            return {
                "success": False,
                "answer": "LLM error",
                "error": str(e)
            }

    # ---------------- SAVE AI MESSAGE ----------------

    ai_message = Message(
        chat_id=chat_id,
        role="assistant",
        content=answer
    )

    db.add(ai_message)

    db.commit()

    return {
        "success": True,
        "chat_id": chat_id,
        "answer": answer,
        "context_used": context
    }