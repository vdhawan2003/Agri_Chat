from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag_core import chat_response  # ✅ import RAG logic
import os
from dotenv import load_dotenv

load_dotenv()
print("🔑 GEMINI_API_KEY loaded:", os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    response = chat_response(request.query)
    return {"reply": response}

@app.get("/")
def home():
    return {"message": "🌿 AgriChat Buddy API is running!"}
