from fastapi import APIRouter
from pydantic import BaseModel

from llm.llama_engine import ask_llm
from rag.retriever import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    context = retrieve_context(request.question)

    if not context:
        return {
            "success": True,
            "answer": "I cannot find relevant information in the uploaded documents.",
            "context_used": []
        }

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

    return {
        "success": True,
        "answer": answer,
        "context_used": context
    }