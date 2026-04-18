FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and seed data
COPY mf_assistant/ ./mf_assistant/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Create data and cache directories
RUN mkdir -p data/raw data/processed data/vector_store /model_cache

# Pre-download the embedding model to avoid startup timeouts
RUN python3 -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5', cache_dir='/model_cache')"

# Set environment variable for fastembed cache
ENV FASTEMBED_CACHE_DIR=/model_cache

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "mf_assistant.main:app", "--host", "0.0.0.0", "--port", "8000"]
