from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    file_hash = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

