from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True) # Firebase UID
    email = Column(String, unique=True, index=True)
    name = Column(String)
    nickname = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    preferred_tone = Column(String, nullable=True)
    support_style = Column(String, nullable=True)
    lifestyle_patterns = Column(String, nullable=True)
    support_network = Column(String, nullable=True)
    education = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True) # UUID string
    user_uid = Column(String, ForeignKey("users.uid"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String) # 'user' or 'bot'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
