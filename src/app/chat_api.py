"""
src/app/chat_api.py
────────────────────
FastAPI backend for MyAlly chat.
Serves the static HTML/CSS/JS frontend and exposes a /chat POST endpoint.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.app.service import chat_logic

app = FastAPI(title="MyAlly Mental-Health Support")

# Serve everything inside /static
_STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.get("/")
async def root():
    return FileResponse(str(_STATIC_DIR / "index.html"))


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        reply = chat_logic(req.message, req.history)
        return {"reply": reply}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
