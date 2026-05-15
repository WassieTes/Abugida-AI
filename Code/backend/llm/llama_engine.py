from pathlib import Path
from llama_cpp import Llama

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "models" / "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,
    n_threads=4
)

def ask_llm(prompt):
    response = llm(
        prompt,
        max_tokens=200
    )

    return response["choices"][0]["text"]