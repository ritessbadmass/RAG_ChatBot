
import os
import sys
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from mf_assistant.config import get_settings
from mf_assistant.rag.rag_service import RAGService

def test_diag():
    settings = get_settings()
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Groq API Key set: {bool(settings.GROQ_API_KEY)}")
    print(f"OpenAI API Key set: {bool(settings.OPENAI_API_KEY)}")
    
    try:
        from mf_assistant.rag.vector_store import VectorStoreService
        vs = VectorStoreService()
        stats = vs.get_stats()
        print(f"Vector Store Stats: {stats}")
    except Exception as e:
        print(f"Vector Store Init Error: {e}")

    try:
        rag = RAGService()
        print("RAG Service initialized successfully")
    except Exception as e:
        print(f"RAG Service Init Error: {e}")

if __name__ == "__main__":
    test_diag()
