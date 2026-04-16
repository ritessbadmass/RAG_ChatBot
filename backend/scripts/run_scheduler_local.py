"""
Local scheduler runner for testing the daily ingestion pipeline.
Simulates GitHub Actions scheduler behavior with comprehensive logging.
"""
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging before any other imports
log_dir = Path(__file__).parent.parent / "data" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 80)
logger.info("LOCAL SCHEDULER RUNNER STARTED")
logger.info("=" * 80)
logger.info(f"Log file: {log_file}")
logger.info(f"Timestamp: {datetime.now().isoformat()}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")


def run_phase(phase_name, phase_func):
    """Run a phase with error handling and logging."""
    logger.info("")
    logger.info("-" * 60)
    logger.info(f"PHASE: {phase_name}")
    logger.info("-" * 60)
    
    start_time = datetime.now()
    
    try:
        result = phase_func()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Phase '{phase_name}' completed successfully in {duration:.2f}s")
        return True, result
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"Phase '{phase_name}' failed after {duration:.2f}s")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return False, str(e)


def phase_1_environment_setup():
    """Phase 1: Environment setup and validation."""
    logger.info("Setting up environment...")
    
    # Check environment variables
    required_vars = [
        'GROQ_API_KEY',
        'CHROMA_CLOUD_TOKEN',
        'CHROMA_CLOUD_TENANT',
        'CHROMA_CLOUD_DATABASE'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            logger.info(f"  {var}: {masked}")
        else:
            logger.warning(f"  {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.info("Continuing with local vector store only...")
    
    # Create necessary directories
    data_dir = Path(__file__).parent.parent / "data"
    vector_store_dir = data_dir / "vector_store"
    processed_dir = data_dir / "processed"
    
    for dir_path in [data_dir, vector_store_dir, processed_dir, log_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"  Directory ready: {dir_path}")
    
    logger.info("Environment setup complete")
    return {"missing_vars": missing_vars}


def phase_2_scraping():
    """Phase 2: Scrape mutual fund URLs."""
    logger.info("Starting scraping phase...")
    
    from mf_assistant.config import MUTUAL_FUND_URLS
    from mf_assistant.services.scraper import MutualFundScraper
    
    scraper = MutualFundScraper()
    
    # Get all URLs
    urls = []
    for amc, schemes in MUTUAL_FUND_URLS.items():
        for scheme_name, url in schemes.items():
            urls.append({
                'url': url,
                'amc': amc,
                'scheme': scheme_name
            })
    
    logger.info(f"Found {len(urls)} URLs to scrape")
    
    scraped_data = []
    errors = []
    
    for i, config in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] Scraping: {config['amc']} - {config['scheme']}")
        logger.info(f"  URL: {config['url']}")
        
        try:
            result = scraper.scrape_url(config['url'])
            
            if result.error:
                logger.error(f"  Error: {result.error}")
                errors.append({
                    'amc': config['amc'],
                    'scheme': config['scheme'],
                    'error': result.error
                })
            else:
                scraped_data.append(result)
                logger.info(f"  Success! Extracted {len(result.extracted_fields)} fields")
                logger.info(f"  Fund: {result.fund_name}")
                content_length = len(result.raw_text) if result.raw_text else 0
                logger.info(f"  Content length: {content_length} chars")
                
        except Exception as e:
            logger.error(f"  Exception: {str(e)}")
            errors.append({
                'amc': config['amc'],
                'scheme': config['scheme'],
                'error': str(e)
            })
    
    logger.info(f"Scraping complete: {len(scraped_data)} successful, {len(errors)} errors")
    
    return {
        'scraped_data': scraped_data,
        'errors': errors,
        'total_urls': len(urls),
        'successful': len(scraped_data),
        'failed': len(errors)
    }


def phase_3_chunking(scraped_data):
    """Phase 3: Chunk documents."""
    logger.info("Starting chunking phase...")
    
    from mf_assistant.rag.chunker import DocumentChunker
    
    chunker = DocumentChunker()
    all_chunks = []
    
    for data in scraped_data:
        try:
            chunks = chunker.chunk_document(data)
            all_chunks.extend(chunks)
            logger.info(f"  {data.fund_name}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"  Error chunking {data.fund_name}: {str(e)}")
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    return {
        'chunks': all_chunks,
        'total_chunks': len(all_chunks)
    }


def phase_4_embedding(chunks):
    """Phase 4: Generate embeddings."""
    logger.info("Starting embedding phase...")
    
    from mf_assistant.rag.embedder import EmbeddingService
    from mf_assistant.config import get_settings
    
    settings = get_settings()
    embedder = EmbeddingService()
    
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    logger.info(f"Using model: {embedder.model}")
    logger.info(f"Device: {settings.EMBEDDING_DEVICE}")
    
    try:
        embeddings = embedder.embed_chunks(chunks)
        logger.info(f"Generated {len(embeddings)} embeddings")
        logger.info(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
        return {
            'embeddings': embeddings,
            'count': len(embeddings),
            'dimension': len(embeddings[0]) if embeddings else 0
        }
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise


def phase_5_vector_storage(chunks, embeddings):
    """Phase 5: Store in vector store."""
    logger.info("Starting vector storage phase...")
    
    from mf_assistant.rag.vector_store import VectorStoreService
    
    vector_store = VectorStoreService()
    
    logger.info(f"Vector store type: {'Cloud' if vector_store.using_cloud else 'Local'}")
    logger.info(f"Collection: {vector_store.collection_name}")
    
    try:
        vector_store.add_embeddings(chunks, embeddings)
        logger.info("Embeddings stored successfully")
        
        # Get stats
        stats = vector_store.get_stats()
        logger.info(f"Vector store stats: {stats}")
        
        return {
            'stored': len(chunks),
            'stats': stats,
            'using_cloud': vector_store.using_cloud
        }
        
    except Exception as e:
        logger.error(f"Vector storage failed: {str(e)}")
        raise


def phase_6_verification():
    """Phase 6: Verify results."""
    logger.info("Starting verification phase...")
    
    vector_store_dir = Path(__file__).parent.parent / "data" / "vector_store"
    
    if vector_store_dir.exists():
        size = sum(f.stat().st_size for f in vector_store_dir.rglob('*') if f.is_file())
        logger.info(f"Local vector store size: {size / 1024 / 1024:.2f} MB")
        
        # List files
        files = list(vector_store_dir.rglob('*'))
        logger.info(f"Total files: {len(files)}")
        
        return {
            'local_store_exists': True,
            'size_mb': size / 1024 / 1024,
            'file_count': len(files)
        }
    else:
        logger.info("Local vector store not found (using cloud only)")
        return {
            'local_store_exists': False
        }


def main():
    """Main scheduler runner."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("STARTING INGESTION PIPELINE")
    logger.info("=" * 80)
    
    overall_start = datetime.now()
    results = {}
    
    # Phase 1: Environment Setup
    success, result = run_phase("Environment Setup", phase_1_environment_setup)
    if not success:
        logger.error("Environment setup failed, aborting")
        return 1
    results['environment'] = result
    
    # Phase 2: Scraping
    success, result = run_phase("Scraping", phase_2_scraping)
    if not success:
        logger.error("Scraping failed, aborting")
        return 1
    results['scraping'] = result
    
    if result['successful'] == 0:
        logger.error("No documents scraped successfully, aborting")
        return 1
    
    # Phase 3: Chunking
    success, result = run_phase("Chunking", lambda: phase_3_chunking(results['scraping']['scraped_data']))
    if not success:
        logger.error("Chunking failed, aborting")
        return 1
    results['chunking'] = result
    
    # Phase 4: Embedding
    success, result = run_phase("Embedding", lambda: phase_4_embedding(results['chunking']['chunks']))
    if not success:
        logger.error("Embedding failed, aborting")
        return 1
    results['embedding'] = result
    
    # Phase 5: Vector Storage
    success, result = run_phase("Vector Storage", lambda: phase_5_vector_storage(
        results['chunking']['chunks'],
        results['embedding']['embeddings']
    ))
    if not success:
        logger.error("Vector storage failed, aborting")
        return 1
    results['storage'] = result
    
    # Phase 6: Verification
    success, result = run_phase("Verification", phase_6_verification)
    results['verification'] = result
    
    # Summary
    overall_end = datetime.now()
    total_duration = (overall_end - overall_start).total_seconds()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("INGESTION PIPELINE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total duration: {total_duration:.2f}s")
    logger.info(f"Documents scraped: {results['scraping']['successful']}/{results['scraping']['total_urls']}")
    logger.info(f"Chunks created: {results['chunking']['total_chunks']}")
    logger.info(f"Embeddings generated: {results['embedding']['count']}")
    logger.info(f"Vector store: {'Cloud' if results['storage']['using_cloud'] else 'Local'}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
