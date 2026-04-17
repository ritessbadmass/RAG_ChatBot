"""Pydantic models for request/response validation."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QueryType(str, Enum):
    """Types of user queries."""
    FACTUAL = "factual"
    ADVISORY = "advisory"
    PROCEDURAL = "procedural"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    """Message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, max_length=500, description="User query")
    thread_id: Optional[str] = Field(None, description="Optional thread ID for conversation continuity")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query doesn't contain PII."""
        # Basic PII detection patterns
        pii_patterns = [
            r'\d{4}[\s-]?\d{4}[\s-]?\d{4}',  # PAN-like
            r'\d{12}',  # Aadhaar-like
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
            r'\d{10}',  # Phone-like
        ]
        import re
        for pattern in pii_patterns:
            if re.search(pattern, v):
                raise ValueError("Query contains potential PII. Please remove personal information.")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., max_length=500, description="Answer to user query (max 3 sentences)")
    source_url: str = Field(..., description="Source URL for the information")
    last_updated: str = Field(..., description="Date when source was last updated")
    thread_id: str = Field(..., description="Thread ID for conversation tracking")
    query_type: QueryType = Field(..., description="Type of query processed")
    disclaimer: str = Field(default="Facts-only. No investment advice.")
    
    @field_validator('answer')
    @classmethod
    def validate_answer_length(cls, v: str) -> str:
        """Ensure answer is max 3 sentences."""
        sentences = [s.strip() for s in v.split('.') if s.strip()]
        if len(sentences) > 3:
            raise ValueError("Answer must be maximum 3 sentences")
        return v


class Message(BaseModel):
    """Individual message in a conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[str]] = None


class Thread(BaseModel):
    """Conversation thread model."""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ThreadCreateResponse(BaseModel):
    """Response for thread creation."""
    thread_id: str
    created_at: datetime


class ThreadHistoryResponse(BaseModel):
    """Response for thread history."""
    thread_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


class DocumentStatus(BaseModel):
    """Document ingestion status."""
    total_documents: int
    last_ingested: Optional[datetime]
    vector_store_size: int
    unique_funds: int
    unique_amcs: int


class IngestRequest(BaseModel):
    """Request for document ingestion."""
    urls: List[str] = Field(..., min_length=1, description="List of URLs to ingest")


class IngestResponse(BaseModel):
    """Response for document ingestion."""
    status: str
    documents_processed: int
    errors: Optional[List[str]] = None


class ExtractedData(BaseModel):
    """Extracted data from scraping."""
    source_url: str
    doc_type: Optional[str] = None
    fund_name: Optional[str] = None
    amc_name: Optional[str] = None
    raw_text: Optional[str] = None
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    pdf_path: Optional[str] = None
    scraped_at: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """System statistics response."""
    total_documents: int
    total_threads: int
    vector_store_size: int
    unique_funds: int
    unique_amcs: int


class RefusalResponse(BaseModel):
    """Response for advisory query refusal."""
    answer: str = "I cannot provide investment advice. I can only answer factual questions about mutual fund schemes."
    source_url: str = "https://www.amfiindia.com/investor-corner/information-center/mutual-fund-faq"
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    thread_id: str
    query_type: QueryType = QueryType.ADVISORY
    disclaimer: str = "Facts-only. No investment advice."


class Chunk(BaseModel):
    """Document chunk model."""
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Embedding(BaseModel):
    """Embedding model."""
    chunk_id: str
    vector: List[float]
    model: str
