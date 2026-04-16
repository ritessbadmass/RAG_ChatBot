"""Data ingestion script to scrape and populate vector store."""
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import MUTUAL_FUND_URLS
from app.services.scraper import MutualFundScraper
from app.rag.chunker import DocumentChunker
from app.rag.embedder import EmbeddingService
from app.rag.vector_store import VectorStoreService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_urls():
    """Flatten the URL config into a list."""
    urls = []
    for amc, schemes in MUTUAL_FUND_URLS.items():
        for scheme_name, url in schemes.items():
            urls.append({
                'url': url,
                'amc': amc,
                'scheme': scheme_name
            })
    return urls


def ingest_data():
    """Main ingestion pipeline."""
    logger.info("Starting data ingestion pipeline...")
    
    # Initialize services
    scraper = MutualFundScraper()
    chunker = DocumentChunker()
    embedder = EmbeddingService()
    vector_store = VectorStoreService()
    
    # Get all URLs
    url_configs = get_all_urls()
    logger.info(f"Found {len(url_configs)} URLs to process")
    
    # Scrape all URLs
    scraped_data = []
    for config in url_configs:
        logger.info(f"Scraping: {config['amc']} - {config['scheme']}")
        result = scraper.scrape_url(config['url'])
        
        if result.error:
            logger.error(f"Error scraping {config['url']}: {result.error}")
            continue
            
        scraped_data.append(result)
        logger.info(f"  -> Extracted {len(result.extracted_fields)} fields")
    
    logger.info(f"Successfully scraped {len(scraped_data)} documents")
    
    # Chunk documents
    all_chunks = []
    for data in scraped_data:
        chunks = chunker.chunk_document(data)
        all_chunks.extend(chunks)
        logger.info(f"Created {len(chunks)} chunks for {data.fund_name}")
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    # Generate embeddings
    embeddings = embedder.embed_chunks(all_chunks)
    
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    # Store in vector store
    vector_store.add_embeddings(all_chunks, embeddings)
    
    logger.info("Data ingestion complete!")
    logger.info(f"Total documents: {len(scraped_data)}")
    logger.info(f"Total chunks: {len(all_chunks)}")


if __name__ == "__main__":
    ingest_data()
