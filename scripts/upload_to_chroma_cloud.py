"""Upload local vector store to Chroma Cloud."""
import os
import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_to_chroma_cloud():
    """Upload local vector store to Chroma Cloud."""
    # Get configuration from environment
    chroma_token = os.getenv("CHROMA_CLOUD_TOKEN")
    chroma_tenant = os.getenv("CHROMA_CLOUD_TENANT")
    chroma_database = os.getenv("CHROMA_CLOUD_DATABASE")
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "mutual_fund_docs")
    local_persist_dir = "./data/vector_store"
    
    if not chroma_token or not chroma_tenant or not chroma_database:
        logger.error("CHROMA_CLOUD_TOKEN, CHROMA_CLOUD_TENANT, or CHROMA_CLOUD_DATABASE not set")
        return
    
    logger.info(f"Connecting to Chroma Cloud database: {chroma_database}...")
    
    # Connect to Chroma Cloud
    cloud_client = chromadb.CloudClient(
        api_key=chroma_token,
        tenant=chroma_tenant,
        database=chroma_database
    )
    
    # Get or create collection in cloud
    cloud_collection = cloud_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Check if local vector store exists
    if not Path(local_persist_dir).exists():
        logger.error(f"Local vector store not found at {local_persist_dir}")
        return
    
    logger.info("Reading local vector store...")
    
    # Read local vector store
    local_client = chromadb.PersistentClient(
        path=local_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    local_collection = local_client.get_collection(collection_name)
    
    # Get all data from local collection
    results = local_collection.get()
    
    if not results["ids"]:
        logger.warning("No data found in local collection")
        return
    
    logger.info(f"Found {len(results['ids'])} documents to upload")
    
    # Clear cloud collection first
    try:
        cloud_client.delete_collection(collection_name)
        cloud_collection = cloud_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Cleared existing cloud collection")
    except Exception as e:
        logger.warning(f"Could not clear collection (may not exist): {e}")
    
    # Upload in batches
    batch_size = 100
    total = len(results["ids"])
    
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        
        batch_ids = results["ids"][i:batch_end]
        batch_embeddings = results["embeddings"][i:batch_end] if results["embeddings"] else None
        batch_documents = results["documents"][i:batch_end] if results["documents"] else None
        batch_metadatas = results["metadatas"][i:batch_end] if results["metadatas"] else None
        
        cloud_collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        
        logger.info(f"Uploaded batch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({batch_end}/{total})")
    
    logger.info(f"✅ Successfully uploaded {total} documents to Chroma Cloud!")


if __name__ == "__main__":
    upload_to_chroma_cloud()
