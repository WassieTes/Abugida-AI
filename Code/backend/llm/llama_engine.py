from pathlib import Path

from llama_cpp import Llama


BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
)

llm = Llama(
    model_path=str(MODEL_PATH),

    n_ctx=4096,

    n_threads=4,

    verbose=False
)


# ================= NORMAL RESPONSE =================

def ask_llm(question, context):

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content":
                (
                    "You are an offline AI tutor.\n"
                    "Answer ONLY using the provided context.\n"
                    "If the answer is missing say:\n"
                    "'Not found in document'"
                )
            },

            {
                "role": "user",
                "content":
                (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                )
            }
        ],

        max_tokens=120,

        temperature=0.3,

        stop=[
            "Question:",
            "Context:",
            "<|im_end|>"
        ]
    )

    return response["choices"][0]["message"]["content"]


# ================= STREAMING =================

def stream_llm(question, context):

    stream = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content":
                (
                    "You are an offline AI tutor.\n"
                    "Answer ONLY using the provided context.\n"
                    "If answer is missing say:\n"
                    "'Not found in document'"
                )
            },

            {
                "role": "user",
                "content":
                (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                )
            }
        ],

        stream=True,

        max_tokens=120,

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