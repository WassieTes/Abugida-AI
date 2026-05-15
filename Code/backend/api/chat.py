from fastapi import APIRouter
from pydantic import BaseModel

from llm.llama_engine import ask_llm
from rag.retriever import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


# @router.post("/chat")
# def chat(request: ChatRequest):
#     context = retrieve_context(request.question)

#     prompt = f"""
# You are an educational AI tutor.

# Use the context below to answer the student's question.

# Context:
# {context}

# Question:
# {request.question}

# Answer:
# """

#     answer = ask_llm(prompt)

#     return {
#         "answer": answer
#     }

@router.post("/chat")
def chat(request: ChatRequest):

    context = retrieve_context(request.question)

    if not context:
        return {
            "answer": "No relevant information found in the uploaded PDF."
        }

    prompt = f"""
You are a strict educational AI assistant.

RULES:
- Use ONLY the context below.
- If answer is not in context, say "Not found in document".

Context:
{context}

Question:
{request.question}

Answer:
"""

    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "context": context  # for debugging
    }