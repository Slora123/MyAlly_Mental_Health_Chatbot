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
from src.app.database import init_db, get_db
from src.app.models import User, ChatSession, ChatMessage
from src.app.auth import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database on startup
    init_db()
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
async def get_profile(user: User = Depends(get_current_user)):
    return user

@app.post("/api/user/onboarding")
async def save_onboarding(req: OnboardingRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for key, value in req.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {"status": "success", "user": user}

# ── Chat API ──────────────────────────────────────────────────────────────

@app.get("/api/chats")
async def get_chat_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_uid == user.uid).order_by(ChatSession.updated_at.desc()).all()
    return {"sessions": [{"id": s.id, "title": s.title, "updated_at": s.updated_at} for s in sessions]}

@app.get("/api/chats/{session_id}")
async def get_chat_history(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_uid == user.uid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in session.messages]
    return {"session_id": session.id, "title": session.title, "messages": messages}

@app.post("/chat")
async def chat(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f"📥 Received chat request: {req}")
    try:
        if not req.session_id:
            # Create new session
            title = "Chat: " + req.message[:20] + "..." if len(req.message) > 20 else "Chat: " + req.message
            new_session = ChatSession(id=str(uuid.uuid4()), user_uid=user.uid, title=title)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
        else:
            session_id = req.session_id
            
        session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_uid == user.uid).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Save user message to DB
        user_msg = ChatMessage(session_id=session_id, role="user", content=req.message)
        db.add(user_msg)
        db.commit()

        # Build history format expected by logic: list of [user_msg, bot_msg] pairs
        db.refresh(session)
        history_pairs = []
        current_pair = [None, None]
        for m in session.messages[:-1]: # exclude the one we just added
            if m.role == "user":
                if current_pair[0] is not None:
                    history_pairs.append(current_pair)
                    current_pair = [None, None]
                current_pair[0] = m.content
            elif m.role == "bot":
                current_pair[1] = m.content
                history_pairs.append(current_pair)
                current_pair = [None, None]
        if current_pair[0] is not None or current_pair[1] is not None:
            history_pairs.append(current_pair)

        # Call logic
        reply = chat_logic(req.message, history_pairs, user_profile=user)
        
        # Save bot message to DB
        bot_msg = ChatMessage(session_id=session_id, role="bot", content=reply)
        db.add(bot_msg)
        
        # Update session timestamp
        from datetime import datetime
        session.updated_at = datetime.utcnow()
        db.commit()

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
