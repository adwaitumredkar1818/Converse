from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scripts.pipeline import answer


app = FastAPI(title="DarkKnights Energy RAG API")

# Import and include status router
from api_status import router as status_router
app.include_router(status_router)


# Allow frontend to communicate with backend across all origins and protocols
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_pna_and_cors_headers(request, call_next):
    if request.method == "OPTIONS":
        from fastapi import Response
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "message": "DarkKnights Energy RAG API is running"
    }


@app.get("/")
def get_ui():
    import os
    from fastapi.responses import FileResponse
    ui_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"error": "UI file not found"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        result = answer(request.query)

        return {
            "success": True,
            "query": result["query"],
            "answer": result["answer"],
            "category": result["category"],
            "provider": result["provider"],
            "model": result["model"],
            "latencies_ms": result["latencies_ms"],
            "sources": result["sources"]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }