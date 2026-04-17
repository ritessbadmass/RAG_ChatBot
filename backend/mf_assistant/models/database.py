"""SQLAlchemy database models."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    ForeignKey,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session

from mf_assistant.config import get_settings

Base = declarative_base()


class ThreadModel(Base):
    """Thread database model."""
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    messages = relationship("MessageModel", back_populates="thread", cascade="all, delete-orphan")


class MessageModel(Base):
    """Message database model."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sources = Column(Text, nullable=True)  # JSON string of sources
    
    # Relationship
    thread = relationship("ThreadModel", back_populates="messages")


class DocumentModel(Base):
    """Document tracking model."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # factsheet, sid, kim, etc.
    amc = Column(String, nullable=False)
    scheme = Column(String, nullable=False)
    last_ingested = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String, nullable=True)
    status = Column(String, default="active")  # active, archived, error


# Database engine and session
settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
