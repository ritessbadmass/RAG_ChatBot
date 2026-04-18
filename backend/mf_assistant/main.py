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
    """Trigger seed data ingestion automatically on startup."""
    import threading
    from mf_assistant.rag.pipeline import get_pipeline
    
    def run():
        try:
            logger.info("AUTO-SYNC: Starting background seed ingestion...")
            pipeline = get_pipeline()
            # Passing [] runs Step 0 (Seed Data) instantly
            pipeline.run_full_pipeline([])
            logger.info("AUTO-SYNC: Background seed ingestion completed.")
        except Exception as e:
            logger.error(f"AUTO-SYNC: Failed: {e}")

    threading.Thread(target=run, daemon=True).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Mutual Fund FAQ Assistant...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created")
    
    # Start auto-sync so the bot is smart on boot
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

# CORS middleware - Explicitly allow Vercel frontend and common origins
origins = [
    "https://rag-chat-bot-gztc.vercel.app",
    "https://rag-chat-bot-gztc-git-main-ritessbadmass-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "*" # Fallback for other environments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
