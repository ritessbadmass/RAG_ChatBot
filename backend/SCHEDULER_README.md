# Local Scheduler Runner

## Overview
The `run_scheduler_local.py` script simulates the GitHub Actions daily ingestion scheduler locally with comprehensive logging and phase tracking.

## Features

### 6-Phase Pipeline
1. **Environment Setup** - Validates env vars, creates directories
2. **Scraping** - Scrapes all 25 mutual fund URLs
3. **Chunking** - Splits documents into chunks
4. **Embedding** - Generates BGE embeddings
5. **Vector Storage** - Stores in ChromaDB (local or cloud)
6. **Verification** - Validates results

### Comprehensive Logging
- Log file created in `data/logs/scheduler_YYYYMMDD_HHMMSS.log`
- Console output with timestamps
- Phase duration tracking
- Error details with stack traces

## Usage

### Run the scheduler:
```bash
cd backend
python scripts/run_scheduler_local.py
```

### View logs:
```bash
# Latest log
tail -f data/logs/$(ls -t data/logs/ | head -1)

# Specific log
cat data/logs/scheduler_20260417_001018.log
```

## Log File Location
```
backend/data/logs/
└── scheduler_YYYYMMDD_HHMMSS.log
```

## Sample Output

```
================================================================================
LOCAL SCHEDULER RUNNER STARTED
================================================================================
Log file: C:\...\backend\data\logs\scheduler_20260417_001018.log
Timestamp: 2026-04-17T00:10:18.410429
Python version: 3.14.3

------------------------------------------------------------
PHASE: Environment Setup
------------------------------------------------------------
Setting up environment...
  Directory ready: ...\backend\data
  Directory ready: ...\backend\data\vector_store

------------------------------------------------------------
PHASE: Scraping
------------------------------------------------------------
Starting scraping phase...
Found 25 URLs to scrape
[1/25] Scraping: SBI - portal
  URL: https://www.sbimf.com/...
  Success! Extracted 4 fields
...

============================================================
INGESTION PIPELINE COMPLETE
============================================================
Total duration: 245.32s
Documents scraped: 12/25
Chunks created: 29
Embeddings generated: 29
Vector store: Local
```

## Environment Variables

The scheduler checks for these optional variables:
- `GROQ_API_KEY` - For LLM (optional for ingestion)
- `CHROMA_CLOUD_TOKEN` - For cloud vector store
- `CHROMA_CLOUD_TENANT` - Chroma Cloud tenant
- `CHROMA_CLOUD_DATABASE` - Chroma Cloud database

If not set, it uses local vector store only.

## Troubleshooting

### No logs created
Check directory permissions:
```bash
mkdir -p backend/data/logs
```

### Scraping errors
Many URLs return 404 - this is expected for old AMC websites. The scheduler continues with successful scrapes.

### Embedding fails
Ensure you have enough RAM for BGE model loading (~2GB).

## Comparison with GitHub Actions

| Feature | Local Scheduler | GitHub Actions |
|---------|----------------|----------------|
| Schedule | Manual | Daily at 9:15 AM IST |
| Logs | File + Console | GitHub UI |
| Artifacts | Local folder | GitHub Artifacts |
| Vector Store | Local/Cloud | Cloud preferred |
| Duration | ~4-5 minutes | ~3-4 minutes |

## Next Steps

1. Run scheduler: `python scripts/run_scheduler_local.py`
2. Check logs: `cat data/logs/scheduler_*.log`
3. Verify vector store: `ls -lh data/vector_store/`
4. Upload to Chroma Cloud: `python scripts/upload_to_chroma_cloud.py`
