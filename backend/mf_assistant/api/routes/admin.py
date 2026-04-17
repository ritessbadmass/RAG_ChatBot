"""Admin API routes for system management."""
import logging

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Optional
import datetime

# In-memory status tracking
ingestion_status = {
    "is_running": False,
    "last_run": None,
    "last_result": None,
    "error": None
}

def run_ingestion_task():
    """Background task to run the ingestion pipeline."""
    global ingestion_status
    ingestion_status["is_running"] = True
    ingestion_status["error"] = None
    
    try:
        logger.info("Background ingestion started")
        pipeline = get_pipeline()
        urls_config = build_urls_config()
        stats = pipeline.run_full_pipeline(urls_config)
        
        ingestion_status["last_run"] = datetime.datetime.now().isoformat()
        ingestion_status["last_result"] = stats
        logger.info("Background ingestion completed successfully")
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")
        ingestion_status["error"] = str(e)
    finally:
        ingestion_status["is_running"] = False

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion(background_tasks: BackgroundTasks) -> dict:
    """
    Trigger data ingestion pipeline in the background.
    """
    if ingestion_status["is_running"]:
        return {"status": "already_running", "message": "An ingestion task is already in progress"}
    
    background_tasks.add_task(run_ingestion_task)
    
    return {
        "status": "started",
        "message": "Data ingestion has been started in the background"
    }

@router.get("/ingest/status")
async def get_ingestion_status() -> dict:
    """Get the status of the background ingestion task."""
    return ingestion_status


@router.post("/reset-vector-store", status_code=status.HTTP_200_OK)
async def reset_vector_store() -> dict:
    """
    Reset vector store (delete all data).
    Use with caution!
    """
    try:
        vector_store = VectorStoreService()
        vector_store.reset()
        
        logger.warning("Vector store was reset")
        
        return {
            "status": "reset_complete",
            "message": "Vector store has been cleared"
        }
        
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(e)}"
        )


@router.get("/vector-store-status")
async def vector_store_status() -> dict:
    """Get detailed vector store status."""
    try:
        vector_store = VectorStoreService()
        stats = vector_store.get_stats()
        
        return {
            "status": "active",
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "total_chunks": stats['total_chunks'],
            "unique_sources": stats['unique_sources'],
            "unique_amcs": stats['unique_amcs'],
            "sources": stats.get('sources', []),
            "amcs": stats.get('amcs', [])
        }
        
    except Exception as e:
        logger.error(f"Error getting vector store status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
