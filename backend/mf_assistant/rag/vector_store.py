"""Vector store service using ChromaDB (Local or Cloud)."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from mf_assistant.config import get_settings
from mf_assistant.models.schemas import Chunk
from mf_assistant.core.exceptions import VectorStoreException

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreService:
    """
    Service for managing vector store operations with ChromaDB.
    Supports both local persistence and Chroma Cloud.
    """
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        # Check if using Chroma Cloud
        self.using_cloud = bool(settings.CHROMA_CLOUD_TOKEN and settings.CHROMA_CLOUD_TENANT and settings.CHROMA_CLOUD_DATABASE)
        
        if self.using_cloud:
            try:
                self._init_cloud_client()
                logger.info(f"Initialized Cloud vector store: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Chroma Cloud: {e}. Falling back to local store.")
                self.using_cloud = False
                self._init_local_client()
        else:
            self._init_local_client()
            logger.info(f"Initialized local vector store: {self.collection_name}")
    
    def _init_local_client(self):
        """Initialize local ChromaDB client."""
        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def _init_cloud_client(self):
        """Initialize Chroma Cloud client."""
        self.client = chromadb.CloudClient(
            api_key=settings.CHROMA_CLOUD_TOKEN,
            tenant=settings.CHROMA_CLOUD_TENANT,
            database=settings.CHROMA_CLOUD_DATABASE
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_embeddings(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """
        Add chunks and their embeddings to the vector store.
        
        Args:
            chunks: List of Chunk objects
            embeddings: List of embedding vectors (List[float])
        """
        if len(chunks) != len(embeddings):
            raise VectorStoreException("Chunks and embeddings must have same length")
        
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        logger.info(f"Adding {len(chunks)} chunks to vector store")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embedding_vectors = []
        
        for chunk, embedding in zip(chunks, embeddings):
            ids.append(chunk.id)
            documents.append(chunk.text)
            metadatas.append(chunk.metadata)
            embedding_vectors.append(embedding)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_embeds = embedding_vectors[i:i + batch_size]
            
            self.collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=batch_embeds
            )
            
            logger.debug(f"Added batch {i//batch_size + 1}")
        
        logger.info(f"Successfully added {len(chunks)} chunks to vector store")
    
    def search(self, query_embedding: List[float], n_results: int = 5, 
               filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results with metadata
        """
        logger.debug(f"Searching vector store with filters: {filters}")
        
        # Build where clause for filters
        where_clause = None
        if filters:
            where_clause = self._build_where_clause(filters)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
        
        logger.debug(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def delete_by_source(self, source_url: str) -> None:
        """
        Delete all chunks from a specific source.
        
        Args:
            source_url: Source URL to delete
        """
        logger.info(f"Deleting chunks for source: {source_url}")
        
        self.collection.delete(
            where={"source_url": source_url}
        )
        
        logger.info(f"Deleted chunks for {source_url}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with statistics
        """
        count = self.collection.count()
        
        # Get unique sources
        all_metadata = self.collection.get(include=["metadatas"])
        sources = set()
        amcs = set()
        
        if all_metadata['metadatas']:
            for metadata in all_metadata['metadatas']:
                if 'source_url' in metadata:
                    sources.add(metadata['source_url'])
                if 'amc' in metadata:
                    amcs.add(metadata['amc'])
        
        return {
            'total_chunks': count,
            'unique_sources': len(sources),
            'unique_amcs': len(amcs),
            'sources': list(sources),
            'amcs': list(amcs)
        }
    
    def reset(self) -> None:
        """Reset the collection (delete all data)."""
        logger.warning("Resetting vector store collection")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store reset complete")
    
    def _build_where_clause(self, filters: Dict) -> Dict:
        """Build ChromaDB where clause from filters."""
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, list):
                # OR condition for list values
                conditions.append({
                    "$or": [{key: v} for v in value]
                })
            else:
                conditions.append({key: value})
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"$and": conditions}
        
        return None


class VectorStoreManager:
    """
    Manager for vector store operations with caching.
    """
    
    def __init__(self):
        self._store: Optional[VectorStoreService] = None
    
    def get_store(self) -> VectorStoreService:
        """Get or create vector store service."""
        if self._store is None:
            self._store = VectorStoreService()
        return self._store
    
    def close(self):
        """Close vector store connection."""
        self._store = None
