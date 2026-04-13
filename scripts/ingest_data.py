"""Script to run data ingestion pipeline manually or via scheduler."""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.pipeline import build_urls_config, get_pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the data ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("MUTUAL FUND DATA INGESTION")
    logger.info("=" * 60)
    
    # Build URL configuration
    urls_config = build_urls_config()
    logger.info(f"Found {len(urls_config)} URLs to process")
    
    # Log URLs being processed
    for config in urls_config:
        logger.info(f"  - {config['amc']}: {config['scheme']}")
    
    # Run pipeline
    pipeline = get_pipeline()
    stats = pipeline.run_full_pipeline(urls_config)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"URLs processed: {stats['urls_processed']}")
    logger.info(f"Documents scraped: {stats['documents_scraped']}")
    logger.info(f"Chunks created: {stats['chunks_created']}")
    logger.info(f"Embeddings generated: {stats['embeddings_generated']}")
    
    if stats.get('errors'):
        logger.warning(f"Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.warning(f"  - {error}")
    
    return 0 if not stats.get('errors') else 1


if __name__ == "__main__":
    sys.exit(main())
