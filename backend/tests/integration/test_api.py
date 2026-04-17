"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from mf_assistant.main import mf_assistant


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestChatEndpoint:
    """Test chat endpoint."""
    
    def test_chat_missing_body(self, client):
        """Test chat without body returns 422."""
        response = client.post("/chat")
        assert response.status_code == 422
    
    def test_chat_valid_factual_query(self, client):
        """Test chat with valid factual query."""
        # Note: This requires vector store to be populated
        # Skip if not populated
        response = client.post("/chat", json={
            "query": "What is expense ratio?"
        })
        # Should either succeed or return service unavailable
        assert response.status_code in [200, 503]
    
    def test_chat_advisory_query_rejected(self, client):
        """Test that advisory queries are rejected."""
        response = client.post("/chat", json={
            "query": "Should I invest in this fund?"
        })
        assert response.status_code == 200
        data = response.json()
        assert "cannot provide investment advice" in data["answer"].lower() or \
               data.get("query_type") == "advisory"
    
    def test_chat_pii_rejected(self, client):
        """Test that PII is rejected."""
        response = client.post("/chat", json={
            "query": "My PAN is ABCDE1234F, what is the NAV?"
        })
        assert response.status_code == 400
        assert "PII" in response.json()["detail"]
    
    def test_chat_query_too_long(self, client):
        """Test that long queries are rejected."""
        response = client.post("/chat", json={
            "query": "a" * 501
        })
        assert response.status_code == 422


class TestThreadEndpoints:
    """Test thread management endpoints."""
    
    def test_create_thread(self, client):
        """Test thread creation."""
        response = client.post("/chat/threads")
        assert response.status_code == 201
        data = response.json()
        assert "thread_id" in data
        assert "created_at" in data
    
    def test_get_thread_not_found(self, client):
        """Test getting non-existent thread."""
        response = client.get("/chat/threads/non-existent-id")
        assert response.status_code == 404
    
    def test_get_thread_exists(self, client):
        """Test getting existing thread."""
        # Create thread first
        create_response = client.post("/chat/threads")
        thread_id = create_response.json()["thread_id"]
        
        # Get thread
        response = client.get(f"/chat/threads/{thread_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == thread_id
        assert "messages" in data
    
    def test_delete_thread(self, client):
        """Test thread deletion."""
        # Create thread
        create_response = client.post("/chat/threads")
        thread_id = create_response.json()["thread_id"]
        
        # Delete thread
        response = client.delete(f"/chat/threads/{thread_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/chat/threads/{thread_id}")
        assert get_response.status_code == 404


class TestAdminEndpoints:
    """Test admin endpoints."""
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint."""
        response = client.get("/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "vector_store_size" in data
    
    def test_vector_store_status(self, client):
        """Test vector store status endpoint."""
        response = client.get("/admin/vector-store-status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
