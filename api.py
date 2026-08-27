import os
import json
import uuid
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()

from scripts.pipeline import answer
from api_status import router as status_router

app = FastAPI(title="DarkKnights Energy RAG API")
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
    from fastapi import Response
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# Supabase Client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
sb: Client = create_client(url, key)

# --- Dependencies ---
def get_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        user_res = sb.auth.get_user(token)
        return user_res.user
    except Exception:
        return None

def require_user(user = Depends(get_user_from_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# --- Models ---
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    theme: Optional[str] = None

# --- Routes ---
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "message": "DarkKnights Energy RAG API is running"
    }

@app.get("/")
def get_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"error": "UI file not found"}

@app.get("/chat_ui")
def get_chat_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "frontend", "chat.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"error": "Chat UI file not found"}

@app.get("/register")
def get_register_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "frontend", "register.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"error": "Register UI file not found"}


@app.get("/profile")
def get_profile_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "frontend", "profile.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"error": "Profile UI file not found"}

@app.post("/api/login")
def login(request: LoginRequest):
    try:
        res = sb.auth.sign_in_with_password({"email": request.email, "password": request.password})
        
        # Update last_active_time
        if res.user:
            sb.table("profiles").update({"last_active_time": "now()"}).eq("id", res.user.id).execute()
        
        return {
            "success": True, 
            "session": {
                "access_token": res.session.access_token,
                "user": {"email": res.user.email}
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@app.post("/api/register")
def register(request: RegisterRequest):
    try:
        res = sb.auth.sign_up({"email": request.email, "password": request.password})
        if res.user:
            # Prefill the name in the profile (trigger creates the row)
            import time; time.sleep(0.5)  # slight delay for trigger to fire
            sb.table("profiles").update({"name": request.name}).eq("id", res.user.id).execute()
            return {"success": True}
        return {"success": False, "message": "Could not create user. Email may already be registered."}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/chat")
def chat(request: ChatRequest, user = Depends(get_user_from_token)):
    try:
        session_id = request.session_id
        
        # If user is logged in, handle history tracking
        if user:
            # Create session if needed
            if not session_id:
                # Generate a short title from the query
                title = request.query[:40] + ("..." if len(request.query) > 40 else "")
                session_res = sb.table("chat_sessions").insert({
                    "user_id": user.id,
                    "title": title
                }).execute()
                session_id = session_res.data[0]["id"]
            
            # Save User Message
            sb.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user.id,
                "role": "user",
                "content": request.query
            }).execute()

        # Generate RAG response
        result = answer(request.query)

        if user and session_id:
            # Save Assistant Message
            sb.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user.id,
                "role": "assistant",
                "content": result["answer"]
            }).execute()

            # Update user stats
            profile_res = sb.table("profiles").select("total_queries").eq("id", user.id).execute()
            if profile_res.data:
                current = profile_res.data[0].get("total_queries", 0)
                sb.table("profiles").update({"total_queries": current + 1}).eq("id", user.id).execute()

        return {
            "success": True,
            "session_id": session_id,
            "query": result["query"],
            "answer": result["answer"],
            "category": result["category"],
            "provider": result["provider"],
            "model": result["model"],
            "latencies_ms": result["latencies_ms"],
            "sources": result["sources"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/chats")
def get_chats(user = Depends(require_user)):
    try:
        # Fetch sessions ordered by newest first
        res = sb.table("chat_sessions").select("id, title, created_at").eq("user_id", user.id).order("created_at", desc=True).execute()
        return {"success": True, "sessions": res.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/chats/{session_id}")
def get_chat_messages(session_id: str, user = Depends(require_user)):
    try:
        # Ensure the session belongs to the user
        session_res = sb.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user.id).execute()
        if not session_res.data:
            return {"success": False, "error": "Session not found or access denied."}
            
        res = sb.table("chat_messages").select("role, content, created_at").eq("session_id", session_id).order("created_at").execute()
        return {"success": True, "messages": res.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/chats/{session_id}")
def delete_chat_session(session_id: str, user = Depends(require_user)):
    try:
        # Ensure the session belongs to the user before deleting
        session_res = sb.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user.id).execute()
        if not session_res.data:
            return {"success": False, "error": "Session not found or access denied."}
            
        sb.table("chat_sessions").delete().eq("id", session_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/profile")
def get_profile(user = Depends(require_user)):
    profile_res = sb.table("profiles").select("*").eq("id", user.id).execute()
    if profile_res.data:
        return {"success": True, "profile": profile_res.data[0]}
    return {"success": False, "message": "Profile not found"}

@app.post("/api/profile")
def update_profile(data: ProfileUpdate, user = Depends(require_user)):
    update_data = {}
    if data.name is not None: update_data["name"] = data.name
    if data.role is not None: update_data["role"] = data.role
    if data.department is not None: update_data["department"] = data.department
    if data.theme is not None: update_data["theme"] = data.theme
    
    sb.table("profiles").update(update_data).eq("id", user.id).execute()
    return {"success": True}

@app.post("/api/profile/apikey")
def generate_apikey(user = Depends(require_user)):
    new_key = "vq_" + uuid.uuid4().hex
    
    # fetch current keys
    profile_res = sb.table("profiles").select("api_keys").eq("id", user.id).execute()
    keys = profile_res.data[0].get("api_keys", []) if profile_res.data else []
    keys.append(new_key)
    
    sb.table("profiles").update({"api_keys": keys}).eq("id", user.id).execute()
    return {"success": True, "api_key": new_key}

@app.get("/api/profile/export")
def export_profile(user = Depends(require_user)):
    profile_res = sb.table("profiles").select("*").eq("id", user.id).execute()
    profile_data = profile_res.data[0] if profile_res.data else {}
    
    json_data = json.dumps(profile_data, indent=2)
    return Response(
        content=json_data, 
        media_type="application/json", 
        headers={"Content-Disposition": f"attachment; filename=profile_{user.email}.json"}
    )