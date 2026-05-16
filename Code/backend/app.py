from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router

from api.upload import router as upload_router

from api.documents import router as documents_router

from database.init_db import init_database

from rag.vector_store import load_store

app = FastAPI()


# ================= DATABASE =================

init_database()


# ================= VECTOR STORE =================

load_store()


# ================= CORS =================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ================= ROUTES =================

app.include_router(chat_router)

app.include_router(upload_router)

app.include_router(documents_router)


# ================= ROOT =================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "Offline AI Tutor Backend Running"
    }