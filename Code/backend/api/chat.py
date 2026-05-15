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

    # HARD FAIL SAFE
    if not context or context.strip() == "":
        return {
            "answer": "I cannot find relevant information in the uploaded documents.",
            "context_used": []
        }

    # STRICT PROMPT (this is very important for accuracy)
    prompt = f"""
You are an offline AI educational tutor.

STRICT RULES:
- Use ONLY the provided context.
- Do NOT use outside knowledge.
- If the answer is not in the context, say: "Not found in document."
- Keep answers simple and educational.

CONTEXT:
{context}

QUESTION:
{request.question}

FINAL ANSWER:
"""

    try:
        answer = ask_llm(prompt)
    except Exception as e:
        return {
            "answer": "Error while generating response from LLM.",
            "error": str(e)
        }

    return {
        "answer": answer,
        "context_used": context
    }