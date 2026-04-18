"""Embedding service for document chunks using local BGE model."""
import logging
from typing import List

from fastembed import TextEmbedding

from mf_assistant.config import get_settings
from mf_assistant.models.schemas import Chunk

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Service for generating embeddings using local fastembed (low memory).
    """
    
    def __init__(self, model: str = None):
        self.model_name = model or settings.EMBEDDING_MODEL
        # Use the pre-downloaded cache directory from Dockerfile
        self.client = TextEmbedding(
            model_name=self.model_name,
            cache_dir="/model_cache"
        )
        logger.info(f"Initialized fastembed service with model: {self.model_name} (using pre-baked cache)")
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        Generate embeddings for a list of chunks.
        """
        if not chunks:
            return []
        
        texts = [chunk.text for chunk in chunks]
        # fastembed returns a generator, convert to list of lists
        embeddings = list(self.client.embed(texts))
        return [emb.tolist() for emb in embeddings]
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.
        """
        # query_embed handles retrieval-specific prefixes if needed
        embeddings = list(self.client.query_embed(query))
        return embeddings[0].tolist()
    
    def embed_chunks_batch(self, chunks: List[Chunk], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings in batches to handle large datasets.
        
        Args:
            chunks: List of Chunk objects
            batch_size: Number of chunks to process at once
            
        Returns:
            List of embedding vectors (List[float])
        """
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            vectors = self.embed_chunks(batch)
            all_embeddings.extend(vectors)
        
        return all_embeddings
