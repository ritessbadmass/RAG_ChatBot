"""Embedding service for document chunks using local BGE model."""
import logging
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings

from mf_assistant.config import get_settings
from mf_assistant.models.schemas import Chunk

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Service for generating embeddings using local BGE model (free).
    """
    
    def __init__(self, model: str = None):
        self.model = model or settings.EMBEDDING_MODEL
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model,
            model_kwargs={'device': settings.EMBEDDING_DEVICE},
            encode_kwargs={'normalize_embeddings': True}  # BGE works better with normalization
        )
        logger.info(f"Initialized embedding service with local model: {self.model}")
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of Chunk objects
            
        Returns:
            List of embedding vectors (List[float])
        """
        if not chunks:
            return []
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        # Extract texts
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings using local BGE model
        vectors = self.embeddings.embed_documents(texts)
        
        logger.info(f"Generated {len(vectors)} embeddings using {self.model}")
        return vectors
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        logger.debug(f"Generating embedding for query: {query[:50]}...")
        return self.embeddings.embed_query(query)
    
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
