"""Thread management service for chat history."""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.database import ThreadModel, MessageModel, get_db
from app.models.schemas import Message, MessageRole, Thread

logger = logging.getLogger(__name__)


class ThreadManager:
    """
    Manages chat threads and message history.
    Uses SQLite for persistence.
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def _get_db(self) -> Session:
        """Get database session."""
        if self.db:
            return self.db
        # Create new session
        from app.models.database import SessionLocal
        return SessionLocal()
    
    def create_thread(self) -> Thread:
        """
        Create a new chat thread.
        
        Returns:
            New Thread object
        """
        thread_id = str(uuid.uuid4())
        
        db = self._get_db()
        try:
            db_thread = ThreadModel(
                id=thread_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_thread)
            db.commit()
            
            logger.info(f"Created new thread: {thread_id}")
            
            return Thread(
                id=thread_id,
                created_at=db_thread.created_at,
                updated_at=db_thread.updated_at,
                messages=[]
            )
        finally:
            if not self.db:
                db.close()
    
    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """
        Get thread by ID with all messages.
        
        Args:
            thread_id: Thread UUID
            
        Returns:
            Thread object or None if not found
        """
        db = self._get_db()
        try:
            db_thread = db.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
            
            if not db_thread:
                return None
            
            # Convert messages
            messages = []
            for msg in db_thread.messages:
                sources = json.loads(msg.sources) if msg.sources else None
                messages.append(Message(
                    role=MessageRole(msg.role),
                    content=msg.content,
                    timestamp=msg.timestamp,
                    sources=sources
                ))
            
            return Thread(
                id=db_thread.id,
                created_at=db_thread.created_at,
                updated_at=db_thread.updated_at,
                messages=messages
            )
        finally:
            if not self.db:
                db.close()
    
    def add_message(
        self,
        thread_id: str,
        role: MessageRole,
        content: str,
        sources: Optional[List[str]] = None
    ) -> Message:
        """
        Add a message to a thread.
        
        Args:
            thread_id: Thread ID
            role: Message role (user/assistant/system)
            content: Message content
            sources: Optional source URLs
            
        Returns:
            Created Message object
        """
        db = self._get_db()
        try:
            # Check thread exists
            db_thread = db.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
            if not db_thread:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Create message
            message_id = str(uuid.uuid4())
            db_message = MessageModel(
                id=message_id,
                thread_id=thread_id,
                role=role.value,
                content=content,
                timestamp=datetime.utcnow(),
                sources=json.dumps(sources) if sources else None
            )
            db.add(db_message)
            
            # Update thread timestamp
            db_thread.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.debug(f"Added message to thread {thread_id}")
            
            return Message(
                role=role,
                content=content,
                timestamp=db_message.timestamp,
                sources=sources
            )
        finally:
            if not self.db:
                db.close()
    
    def get_thread_history(self, thread_id: str, limit: int = 10) -> List[Message]:
        """
        Get recent message history for a thread.
        
        Args:
            thread_id: Thread ID
            limit: Maximum number of messages to return
            
        Returns:
            List of Message objects
        """
        thread = self.get_thread(thread_id)
        if not thread:
            return []
        
        # Return last N messages
        return thread.messages[-limit:] if thread.messages else []
    
    def get_formatted_history(self, thread_id: str, limit: int = 5) -> List[Dict]:
        """
        Get formatted history for LLM context.
        
        Args:
            thread_id: Thread ID
            limit: Number of recent exchanges to include
            
        Returns:
            List of message dicts for LLM
        """
        messages = self.get_thread_history(thread_id, limit=limit * 2)
        
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return formatted
    
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread and all its messages.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            True if deleted, False if not found
        """
        db = self._get_db()
        try:
            db_thread = db.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
            
            if not db_thread:
                return False
            
            db.delete(db_thread)
            db.commit()
            
            logger.info(f"Deleted thread: {thread_id}")
            return True
        finally:
            if not self.db:
                db.close()
    
    def list_threads(self, limit: int = 100) -> List[Dict]:
        """
        List all threads (for admin purposes).
        
        Args:
            limit: Maximum threads to return
            
        Returns:
            List of thread summaries
        """
        db = self._get_db()
        try:
            threads = db.query(ThreadModel).order_by(
                ThreadModel.updated_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": t.id,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
                    "message_count": len(t.messages)
                }
                for t in threads
            ]
        finally:
            if not self.db:
                db.close()
    
    def get_stats(self) -> Dict:
        """
        Get thread statistics.
        
        Returns:
            Statistics dict
        """
        db = self._get_db()
        try:
            from sqlalchemy import func
            
            thread_count = db.query(ThreadModel).count()
            message_count = db.query(MessageModel).count()
            
            return {
                "total_threads": thread_count,
                "total_messages": message_count,
                "avg_messages_per_thread": message_count / thread_count if thread_count > 0 else 0
            }
        finally:
            if not self.db:
                db.close()


# Singleton instance
_manager: Optional[ThreadManager] = None


def get_thread_manager() -> ThreadManager:
    """Get or create thread manager instance."""
    global _manager
    if _manager is None:
        _manager = ThreadManager()
    return _manager
