"""
src/app/chat_api.py
────────────────────
FastAPI backend for MyAlly chat.
Serves the static HTML/CSS/JS frontend and exposes a /chat POST endpoint.
"""
from __future__ import annotations

from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from src.app.service import chat_logic
from src.app.auth import get_current_user
from . import vector_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # No SQL DB to initialize anymore
    yield

app = FastAPI(title="MyAlly Mental-Health Support", lifespan=lifespan)

# Serve everything inside frontend/dist
_STATIC_DIR = Path(__file__).resolve().parents[3] / "frontend" / "dist"
app.mount("/assets", StaticFiles(directory=str(_STATIC_DIR / "assets")), name="assets")

class OnboardingRequest(BaseModel):
    nickname: str = None
    gender: str = None
    preferred_tone: str = None
    support_style: str = None
    lifestyle_patterns: str = None
    support_network: str = None
    education: str = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None # If None, creates a new session

@app.get("/")
async def root():
    return FileResponse(str(_STATIC_DIR / "index.html"))

# ── User API ──────────────────────────────────────────────────────────────

@app.get("/api/user/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    return user

@app.post("/api/user/onboarding")
async def save_onboarding(req: OnboardingRequest, user: dict = Depends(get_current_user)):
    profile_data = req.dict(exclude_unset=True)
    updated_user = vector_db.save_user_profile(user["uid"], profile_data)
    return {"status": "success", "user": updated_user}

# ── Chat API ──────────────────────────────────────────────────────────────

@app.get("/api/chats")
async def get_chat_sessions(user: dict = Depends(get_current_user)):
    sessions = vector_db.get_user_sessions(user["uid"])
    return {"sessions": sessions}

@app.get("/api/chats/{session_id}")
async def get_chat_history(session_id: str, user: dict = Depends(get_current_user)):
    session = vector_db.get_session(session_id, user["uid"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = vector_db.get_chat_history(session_id)
    return {"session_id": session_id, "title": session["title"], "messages": messages}

@app.post("/chat")
async def chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    print(f"📥 Received chat request: {req}")
    try:
        if not req.session_id:
            # Create new session
            title = "Chat: " + req.message[:20] + "..." if len(req.message) > 20 else "Chat: " + req.message
            session = vector_db.create_chat_session(user["uid"], title)
            session_id = session["id"]
        else:
            session_id = req.session_id
            session = vector_db.get_session(session_id, user["uid"])
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

        # Save user message to DB
        vector_db.add_chat_message(session_id, role="user", content=req.message)

        # Build history format expected by logic: list of [user_msg, bot_msg] pairs
        full_history = vector_db.get_chat_history(session_id)
        
        history_pairs = []
        current_pair = [None, None]
        # Exclude the message we just added for the 'history' argument to chat_logic
        for m in full_history[:-1]: 
            if m["role"] == "user":
                if current_pair[0] is not None:
                    history_pairs.append(current_pair)
                    current_pair = [None, None]
                current_pair[0] = m["content"]
            elif m["role"] == "bot":
                current_pair[1] = m["content"]
                history_pairs.append(current_pair)
                current_pair = [None, None]
        if current_pair[0] is not None or current_pair[1] is not None:
            history_pairs.append(current_pair)

        # Call logic
        reply = chat_logic(req.message, history_pairs, user_profile=user)
        
        # Save bot message to DB
        vector_db.add_chat_message(session_id, role="bot", content=reply)
        
        return {"reply": reply, "session_id": session_id}
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(exc)})


# ── Admin/Counselor Endpoints ──────────────────────────────────────────────

@app.get("/api/admin/alerts")
async def get_alerts():
    """Fetches all crisis alerts for the counselor."""
    from src.app import counselor_service
    alerts = counselor_service.get_all_alerts()
    return {"alerts": alerts}


@app.post("/api/admin/resolve/{alert_id}")
async def resolve_alert(alert_id: str):
    """Marks a crisis alert as resolved."""
    from src.app import counselor_service
    success = counselor_service.resolve_alert(alert_id)
    if success:
        return {"status": "success"}
    return JSONResponse(status_code=404, content={"error": "Alert not found"})


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
