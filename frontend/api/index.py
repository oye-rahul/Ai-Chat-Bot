import os
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
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


def get_frontend_file(filename: str):
    """Find and read frontend static files from multiple potential deployment locations."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "..", filename),
        os.path.join(base_dir, filename),
        os.path.join(os.getcwd(), "frontend", filename),
        os.path.join(os.getcwd(), "public", filename),
        os.path.join(os.getcwd(), filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return None


# -------------------------------------------------------------
# Static Frontend Routes (renders the chatbot UI directly)
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/frontend", response_class=HTMLResponse)
@app.get("/frontend/", response_class=HTMLResponse)
@app.get("/frontend/index.html", response_class=HTMLResponse)
async def serve_index():
    content = get_frontend_file("index.html")
    if content:
        return HTMLResponse(content=content)
    return HTMLResponse("<h2>Chatbot Frontend Loaded</h2><p>index.html not found</p>", status_code=404)


@app.get("/style.css")
@app.get("/frontend/style.css")
async def serve_style():
    content = get_frontend_file("style.css")
    if content:
        return Response(content=content, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/script.js")
@app.get("/frontend/script.js")
async def serve_script():
    content = get_frontend_file("script.js")
    if content:
        return Response(content=content, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")


# -------------------------------------------------------------
# Backend API Routes
# -------------------------------------------------------------
@app.get("/api/health")
@app.get("/health")
@app.get("/frontend/health")
@app.get("/frontend/api/health")
async def health():
    return {
        "status": "ok",
        "model": model_name,
        "api_key_configured": bool(api_key),
    }


@app.post("/api/chat")
@app.post("/chat")
@app.post("/frontend/chat")
@app.post("/frontend/api/chat")
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


@app.api_route("/api/index.py", methods=["GET", "POST"])
@app.api_route("/frontend/api/index.py", methods=["GET", "POST"])
async def vercel_endpoint_dispatcher(request: Request):
    """Handle Vercel rewrites that route requests to index.py directly."""
    matched = request.headers.get("x-matched-path", "")
    full_url = str(request.url)

    if "health" in matched or "health" in full_url:
        return await health()

    if request.method == "POST":
        try:
            body = await request.json()
            return await chat(ChatRequest(**body))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if "style.css" in matched or "style.css" in full_url:
        return await serve_style()
    if "script.js" in matched or "script.js" in full_url:
        return await serve_script()

    return await serve_index()

