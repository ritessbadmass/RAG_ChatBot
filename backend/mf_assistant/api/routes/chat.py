"""Chat API routes."""
import logging
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from mf_assistant.config import get_settings
from mf_assistant.core.exceptions import AdvisoryQueryException, PIIDetectedException
from mf_assistant.models.database import get_db
from mf_assistant.models.schemas import (
    ChatRequest,
    ChatResponse,
    MessageRole,
    RefusalResponse,
)
from mf_assistant.rag.rag_service import get_rag_service
from mf_assistant.services.query_classifier import get_classifier
from mf_assistant.services.thread_manager import get_thread_manager
from mf_assistant.utils.validators import detect_pii, validate_query_length

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Main chat endpoint for mutual fund Q&A.
    
    - Validates query (length, PII)
    - Classifies query type
    - Rejects advisory queries
    - Retrieves context and generates response
    - Stores conversation history
    """
    query = request.query.strip()
    
    # Step 1: Validate query length
    if not validate_query_length(query):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query must be between 1 and {settings.MAX_QUERY_LENGTH} characters"
        )
    
    # Step 2: Check for PII
    pii_type = detect_pii(query)
    if pii_type:
        logger.warning(f"PII detected: {pii_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query contains potential PII ({pii_type}). Please remove personal information."
        )
    
    # Step 3: Get or create thread (Self-healing logic)
    thread_manager = get_thread_manager()
    thread_id = request.thread_id
    
    if thread_id:
        thread = thread_manager.get_thread(thread_id)
        if not thread:
            logger.warning(f"Thread {thread_id} not found. Automatically creating a new session.")
            thread = thread_manager.create_thread()
            thread_id = thread.id
    else:
        thread = thread_manager.create_thread()
        thread_id = thread.id
    
    # Update request thread_id for consistency
    request.thread_id = thread_id
    
    # Step 4: Add user message to history
    thread_manager.add_message(
        thread_id=thread_id,
        role=MessageRole.USER,
        content=query
    )
    
    try:
        # Step 5: Get thread history for context
        history = thread_manager.get_formatted_history(thread_id, limit=5)
        
        # Step 6: Process query through RAG
        rag_service = get_rag_service()
        result = rag_service.process_query(query, thread_history=history)
        
        # Step 7: Add assistant response to history
        thread_manager.add_message(
            thread_id=thread_id,
            role=MessageRole.ASSISTANT,
            content=result["answer"],
            sources=result.get("sources", [result["source_url"]])
        )
        
        # Step 8: Return response
        return ChatResponse(
            answer=result["answer"],
            source_url=result["source_url"],
            last_updated=result.get("last_updated", "2024-01-01"),
            thread_id=thread_id,
            query_type=result["query_type"],
            disclaimer=settings.DISCLAIMER
        )
        
    except AdvisoryQueryException:
        # Return refusal response for advisory queries
        return RefusalResponse(thread_id=thread_id)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error processing query: {e}\n{error_trace}")
        
        error_detail = str(e)
        if "api_key" in error_detail.lower():
            error_detail = "LLM API Key missing or invalid. Please check your environment variables."
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend Error: {error_detail}"
        )


@router.post("/threads", status_code=status.HTTP_201_CREATED)
async def create_thread() -> dict:
    """Create a new chat thread."""
    thread_manager = get_thread_manager()
    thread = thread_manager.create_thread()
    
    return {
        "thread_id": thread.id,
        "created_at": thread.created_at.isoformat()
    }


@router.get("/threads/{thread_id}")
async def get_thread_history(thread_id: str) -> dict:
    """Get chat history for a thread."""
    thread_manager = get_thread_manager()
    thread = thread_manager.get_thread(thread_id)
    
    if not thread:
        logger.warning(f"Thread {thread_id} not found. Returning fresh thread skeleton.")
        return {
            "thread_id": thread_id,
            "messages": [],
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
    
    return {
        "thread_id": thread.id,
        "created_at": thread.created_at.isoformat(),
        "updated_at": thread.updated_at.isoformat(),
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "sources": msg.sources
            }
            for msg in thread.messages
        ]
    }


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: str):
    """Delete a chat thread."""
    thread_manager = get_thread_manager()
    success = thread_manager.delete_thread(thread_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found"
        )


@router.get("/threads")
async def list_threads(limit: int = 50) -> dict:
    """List all chat threads."""
    thread_manager = get_thread_manager()
    threads = thread_manager.list_threads(limit=limit)
    
    return {
        "threads": threads,
        "total": len(threads)
    }
