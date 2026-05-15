from fastapi import FastAPI
from api.chat import router as chat_router
from api.upload import router as upload_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(upload_router)


@app.get("/")
def root():
    return {"message": "Offline AI Tutor Backend Running"}