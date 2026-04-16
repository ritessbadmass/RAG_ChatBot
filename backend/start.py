"""Startup script for the Mutual Fund FAQ Assistant."""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if environment is properly configured."""
    from mf_assistant.config import get_settings
    
    settings = get_settings()
    
    # Check LLM configuration based on provider
    if settings.LLM_PROVIDER == "groq":
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == 'gsk-your-groq-api-key-here':
            logger.error("GROQ_API_KEY not configured!")
            logger.error("Please set it in your .env file or environment variables.")
            return False
        logger.info("✓ Groq API configured")
    else:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'sk-your-openai-api-key-here':
            logger.error("OPENAI_API_KEY not configured!")
            logger.error("Please set it in your .env file or environment variables.")
            return False
        logger.info("✓ OpenAI API configured")
    
    logger.info(f"✓ Using {settings.LLM_PROVIDER} as LLM provider")
    return True


def check_vector_store():
    """Check if vector store exists."""
    vector_store_path = Path("./data/vector_store")
    
    if not vector_store_path.exists() or not any(vector_store_path.iterdir()):
        logger.warning("Vector store not found or empty!")
        logger.warning("Run: python scripts/ingest_data.py")
        return False
    
    logger.info("✓ Vector store exists")
    return True


def run_ingestion():
    """Run data ingestion."""
    logger.info("Running data ingestion...")
    from scripts.ingest_data import main
    return main()


def run_server():
    """Run the FastAPI server."""
    import uvicorn
    from mf_assistant.config import get_settings
    
    settings = get_settings()
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "mf_assistant.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )


def main():
    parser = argparse.ArgumentParser(
        description="Mutual Fund FAQ Assistant"
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run data ingestion before starting server"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check environment and exit"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Mutual Fund FAQ Assistant")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        return 1
    
    if args.check:
        check_vector_store()
        return 0
    
    # Run ingestion if requested
    if args.ingest:
        if run_ingestion() != 0:
            logger.error("Ingestion failed!")
            return 1
    
    # Check vector store
    check_vector_store()
    
    # Start server
    print("\n" + "=" * 60)
    print("Starting server...")
    print("API docs available at: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    run_server()
    return 0


if __name__ == "__main__":
    sys.exit(main())
