"""FastAPI application main entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mf_assistant.api.routes import chat, admin
from mf_assistant.config import get_settings
from mf_assistant.models.database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


def start_background_sync():
    """Trigger data ingestion on startup."""
    import threading
    from mf_assistant.rag.pipeline import get_pipeline, build_urls_config
    
    def run():
        try:
            # Seed data is now handled synchronously in lifespan for reliability
            # This background thread now handles the heavier web scraping
            logger.info("AUTO-SYNC: Starting background web scraping...")
            pipeline = get_pipeline()
            pipeline.run_full_pipeline(build_urls_config())
            logger.info("AUTO-SYNC: Background web scraping completed.")
        except Exception as e:
            logger.error(f"AUTO-SYNC: Web scraping failed: {e}")

    threading.Thread(target=run, daemon=True).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Mutual Fund FAQ Assistant...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created")
    
    # LOAD SEED DATA IMMEDIATELY (Fail-safe)
    try:
        from mf_assistant.rag.pipeline import get_pipeline
        pipeline = get_pipeline()
        logger.info("AUTO-SYNC: Loading synchronous seed facts...")
        # Passing an empty list to run_full_pipeline only runs the Seed Data step
        pipeline.run_full_pipeline([])
        logger.info("AUTO-SYNC: Seed facts loaded successfully.")
    except Exception as e:
        logger.error(f"AUTO-SYNC: Synchronous seed load failed: {e}")
    
    # Start web scraping in background
    start_background_sync()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Facts-only Q&A assistant for Indian mutual fund schemes",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Root level health checks
@app.get("/health")
@app.get("/ping")
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}

# Include routers
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Facts-only Q&A assistant for Indian mutual fund schemes",
        "docs": "/docs",
        "health": "/admin/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "mf_assistant.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
