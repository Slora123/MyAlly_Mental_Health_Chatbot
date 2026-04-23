"""
backend/src/app/vector_db.py
───────────────────────────
Handles storing and retrieving user profiles, chat sessions, and messages in ChromaDB.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
import chromadb
from pathlib import Path
from src.rag.embeddings import get_embedding_function

# Config
DB_PATH = str(Path(__file__).resolve().parents[3] / "database" / "chroma_db")

# Collection Names
USER_COLLECTION = "user_profiles"
SESSION_COLLECTION = "chat_sessions"
MESSAGE_COLLECTION = "chat_history"

_client = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=DB_PATH)
    return _client

def get_collection(name: str):
    client = get_client()
    ef = get_embedding_function()
    return client.get_or_create_collection(name=name, embedding_function=ef)

# ── User Profile Operations ───────────────────────────────────────────────────

def get_user_profile(uid: str) -> dict | None:
    col = get_collection(USER_COLLECTION)
    result = col.get(ids=[uid])
    if result["ids"]:
        return result["metadatas"][0]
    return None

def save_user_profile(uid: str, profile_data: dict):
    col = get_collection(USER_COLLECTION)
    
    # Merge with existing data if any
    existing = get_user_profile(uid)
    if existing:
        updated_data = {**existing, **profile_data}
    else:
        updated_data = {**profile_data, "uid": uid, "created_at": datetime.utcnow().isoformat()}
    
    col.upsert(
        ids=[uid],
        metadatas=[updated_data],
        documents=[f"Profile for {updated_data.get('name', 'User')}" ]
    )
    return updated_data

# ── Chat Session Operations ──────────────────────────────────────────────────

def get_user_sessions(user_uid: str) -> list[dict]:
    col = get_collection(SESSION_COLLECTION)
    # Chroma doesn't support complex sorting easily in get(), we'll fetch and sort in Python
    results = col.get(
        where={"user_uid": user_uid}
    )
    
    sessions = []
    for i in range(len(results["ids"])):
        sessions.append({
            "id": results["ids"][i],
            **results["metadatas"][i]
        })
    
    # Sort by updated_at descending
    sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return sessions

def create_chat_session(user_uid: str, title: str) -> dict:
    col = get_collection(SESSION_COLLECTION)
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    session_data = {
        "user_uid": user_uid,
        "title": title,
        "created_at": now,
        "updated_at": now
    }
    
    col.add(
        ids=[session_id],
        metadatas=[session_data],
        documents=[title]
    )
    session_data["id"] = session_id
    return session_data

def get_session(session_id: str, user_uid: str) -> dict | None:
    col = get_collection(SESSION_COLLECTION)
    result = col.get(ids=[session_id], where={"user_uid": user_uid})
    if result["ids"]:
        data = result["metadatas"][0]
        data["id"] = session_id
        return data
    return None

def update_session_timestamp(session_id: str):
    col = get_collection(SESSION_COLLECTION)
    result = col.get(ids=[session_id])
    if result["ids"]:
        data = result["metadatas"][0]
        data["updated_at"] = datetime.utcnow().isoformat()
        col.update(ids=[session_id], metadatas=[data])

# ── Chat Message Operations ──────────────────────────────────────────────────

def add_chat_message(session_id: str, role: str, content: str):
    col = get_collection(MESSAGE_COLLECTION)
    message_id = f"{session_id}_{datetime.utcnow().timestamp()}_{uuid.uuid4().hex[:4]}"
    
    metadata = {
        "session_id": session_id,
        "role": role,
        "created_at": datetime.utcnow().isoformat()
    }
    
    col.add(
        ids=[message_id],
        metadatas=[metadata],
        documents=[content]
    )
    update_session_timestamp(session_id)

def get_chat_history(session_id: str) -> list[dict]:
    col = get_collection(MESSAGE_COLLECTION)
    results = col.get(
        where={"session_id": session_id}
    )
    
    messages = []
    for i in range(len(results["ids"])):
        messages.append({
            "id": results["ids"][i],
            "role": results["metadatas"][i]["role"],
            "content": results["documents"][i],
            "created_at": results["metadatas"][i]["created_at"]
        })
    
    # Sort by created_at
    messages.sort(key=lambda x: x["created_at"])
    return messages
