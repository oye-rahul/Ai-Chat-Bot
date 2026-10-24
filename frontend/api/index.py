import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# Load local .env file if running locally
load_dotenv(find_dotenv())

app = FastAPI(title="Gemini Chatbot API")

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API key (read from Vercel environment variables or .env)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

model = None
if api_key:
    try:
        model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
        )
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini model: {e}")

chat_history = []


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": model_name,
        "api_key_configured": bool(api_key),
    }


@app.post("/api/chat")
@app.post("/chat")
async def chat(req: ChatRequest):
    global model

    # Re-check key in case environment was updated
    current_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not model and current_key:
        model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=current_key,
        )

    if not model:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY is not configured. Please set GOOGLE_API_KEY in Vercel Environment Variables.",
        )

    try:
        chat_history.append(HumanMessage(content=req.message))
        response = model.invoke(chat_history)
        chat_history.append(AIMessage(content=response.content))

        return {
            "response": response.content
        }
    except Exception as e:
        # Prevent appending failed message to keep history clean
        if chat_history and isinstance(chat_history[-1], HumanMessage):
            chat_history.pop()
        raise HTTPException(status_code=500, detail=str(e))
