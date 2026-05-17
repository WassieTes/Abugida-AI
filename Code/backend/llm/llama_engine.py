from pathlib import Path

from llama_cpp import Llama


# =====================================================
# MODEL PATH
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
)


# =====================================================
# LOAD MODEL
# =====================================================

llm = Llama(
    model_path=str(MODEL_PATH),

    n_ctx=4096,

    n_threads=4,

    verbose=False
)


# =====================================================
# BUILD CHAT MESSAGES
# =====================================================

def build_messages(
    question,
    context,
    history=None
):

    messages = [
        {
            "role": "system",
            "content":
            (
                "You are Abugida AI, an offline AI tutor.\n"
                "Answer ONLY using the provided context.\n"
                "Do NOT hallucinate.\n"
                "If answer is not found say:\n"
                "'Not found in document'"
            )
        }
    ]

    # ================= CHAT HISTORY =================

    if history:

        for msg in history:

            messages.append({
                "role": msg.role,
                "content": msg.content
            })

    # ================= CURRENT QUESTION =================

    messages.append({
        "role": "user",
        "content":
        (
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )
    })

    return messages


# =====================================================
# NORMAL RESPONSE
# =====================================================

def ask_llm(
    question,
    context,
    history=None
):

    response = llm.create_chat_completion(

        messages=build_messages(
            question,
            context,
            history
        ),

        max_tokens=180,

        temperature=0.3,

        stop=[
            "Question:",
            "Context:",
            "<|im_end|>"
        ]
    )

    return response["choices"][0]["message"]["content"]


# =====================================================
# STREAMING RESPONSE
# =====================================================

def stream_llm(
    question,
    context,
    history=None
):

    stream = llm.create_chat_completion(

        messages=build_messages(
            question,
            context,
            history
        ),

        stream=True,

        max_tokens=180,

        temperature=0.3,

        stop=[
            "Question:",
            "Context:",
            "<|im_end|>"
        ]
    )

    for chunk in stream:

        delta = chunk["choices"][0]["delta"]

        if "content" in delta:

            yield delta["content"]