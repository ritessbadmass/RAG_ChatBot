"""Data pipeline orchestrator for document ingestion."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.config import MUTUAL_FUND_URLS, get_settings
from app.models.schemas import ExtractedData, Chunk
from app.services.scraper import MutualFundScraper, ScrapingPipeline
from app.rag.chunker import DocumentChunker
from app.rag.embedder import EmbeddingService
from app.rag.vector_store import VectorStoreService

logger = logging.getLogger(__name__)
settings = get_settings()


class DataPipeline:
    """
    Orchestrates the full data pipeline:
    Scrape → Chunk → Embed → Store
    """
    
    def __init__(
        self,
        scraper: Optional[MutualFundScraper] = None,
        chunker: Optional[DocumentChunker] = None,
        embedder: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None
    ):
        self.scraper = scraper or MutualFundScraper()
        self.chunker = chunker or DocumentChunker()
        self.embedder = embedder or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()
    
    def run_full_pipeline(self, urls_config: List[Dict]) -> Dict:
        """
        Run the complete data pipeline.
        
        Args:
            urls_config: List of URL configurations with metadata
            
        Returns:
            Pipeline execution statistics
        """
        logger.info("=" * 60)
        logger.info("STARTING DATA PIPELINE")
        logger.info("=" * 60)
        
        stats = {
            'urls_processed': 0,
            'documents_scraped': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scrape
            logger.info("\n[STEP 1/4] Scraping documents...")
            scraped_data = self._scrape_documents(urls_config)
            stats['documents_scraped'] = len([d for d in scraped_data if not d.error])
            stats['urls_processed'] = len(urls_config)
            
            # Save raw data
            self._save_raw_data(scraped_data)
            
            # Step 2: Chunk
            logger.info("\n[STEP 2/4] Chunking documents...")
            chunks = self._chunk_documents(scraped_data)
            stats['chunks_created'] = len(chunks)
            
            # Step 3: Embed
            logger.info("\n[STEP 3/4] Generating embeddings...")
            embeddings = self._generate_embeddings(chunks)
            stats['embeddings_generated'] = len(embeddings)
            
            # Step 4: Store
            logger.info("\n[STEP 4/4] Storing in vector database...")
            self._store_embeddings(chunks, embeddings)
            
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Documents scraped: {stats['documents_scraped']}")
            logger.info(f"Chunks created: {stats['chunks_created']}")
            logger.info(f"Embeddings stored: {stats['embeddings_generated']}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            stats['errors'].append(str(e))
            raise
        
        return stats
    
    def _scrape_documents(self, urls_config: List[Dict]) -> List[ExtractedData]:
        """Scrape documents from URLs."""
        pipeline = ScrapingPipeline(self.scraper)
        return pipeline.run_pipeline(urls_config)
    
    def _chunk_documents(self, scraped_data: List[ExtractedData]) -> List[Chunk]:
        """Chunk scraped documents."""
        return self.chunker.chunk_documents(scraped_data)
    
    def _generate_embeddings(self, chunks: List[Chunk]) -> List:
        """Generate embeddings for chunks."""
        return self.embedder.embed_chunks_batch(chunks)
    
    def _store_embeddings(self, chunks: List[Chunk], embeddings: List) -> None:
        """Store embeddings in vector database."""
        self.vector_store.add_embeddings(chunks, embeddings)
    
    def _save_raw_data(self, scraped_data: List[ExtractedData]) -> None:
        """Save scraped data to disk for reference."""
        output_dir = Path("./data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        data_dicts = []
        for data in scraped_data:
            data_dict = {
                'source_url': data.source_url,
                'doc_type': data.doc_type,
                'extracted_fields': data.extracted_fields,
                'scraped_at': data.scraped_at,
                'error': data.error
            }
            if hasattr(data, 'metadata'):
                data_dict['metadata'] = data.metadata
            data_dicts.append(data_dict)
        
        output_file = output_dir / "scraped_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved raw data to {output_file}")


def build_urls_config() -> List[Dict]:
    """
    Build URL configuration from MUTUAL_FUND_URLS.
    
    Returns:
        List of URL configurations
    """
    urls_config = []
    
    for amc, schemes in MUTUAL_FUND_URLS.items():
        for scheme_name, url in schemes.items():
            # Detect document type from URL
            doc_type = 'factsheet'  # Default
            if 'etf' in url.lower() or 'bees' in url.lower():
                doc_type = 'factsheet'
            
            config = {
                'url': url,
                'amc': amc,
                'scheme': scheme_name.replace('_', ' ').title(),
                'doc_type': doc_type,
                'category': 'equity'  # Default category
            }
            urls_config.append(config)
    
    return urls_config


# Singleton instance
_pipeline_instance: Optional[DataPipeline] = None


def get_pipeline() -> DataPipeline:
    """Get or create pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DataPipeline()
    return _pipeline_instance
