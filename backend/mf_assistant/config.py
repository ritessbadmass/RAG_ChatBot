"""Application configuration management."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Mutual Fund FAQ Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM Configuration
    LLM_PROVIDER: str = "groq"  # "openai" or "groq"
    
    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Groq (recommended)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    # Local Embeddings (Free - BGE)
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DEVICE: str = "cpu"  # or "cuda" if GPU available
    
    # ChromaDB (Local or Cloud)
    CHROMA_PERSIST_DIRECTORY: str = "./data/vector_store"
    CHROMA_COLLECTION_NAME: str = "mutual_fund_docs"
    
    # Chroma Cloud (optional - for cloud deployment)
    CHROMA_CLOUD_TOKEN: str = ""  # API key from Chroma Cloud
    CHROMA_CLOUD_TENANT: str = ""  # Tenant ID
    CHROMA_CLOUD_DATABASE: str = ""  # Database name
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/chat_history.db"
    
    # Security
    MAX_QUERY_LENGTH: int = 500
    RATE_LIMIT_PER_MINUTE: int = 30
    SECRET_KEY: str = "change-me-in-production"
    
    # Compliance
    DISCLAIMER: str = "Facts-only. No investment advice."
    
    # Scraping
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_RATE_LIMIT_DELAY: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Scraping configuration
SCRAPER_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2,
    "rate_limit_delay": 1,
    "max_pdf_size_mb": 10,
    "allowed_domains": [
        "sbimf.com",
        "icicipruamc.com",
        "hdfcfund.com",
        "nipponindiaim.com",
        "kotakmf.com",
        "amfiindia.com",
        "sebi.gov.in",
        "kuvera.in"
    ],
    "field_priority": {
        "expense_ratio": ["factsheet", "amfi"],
        "exit_load": ["kim", "factsheet"],
        "min_sip_amount": ["kim", "factsheet"],
        "lock_in_period": ["sid", "factsheet"],
        "riskometer": ["factsheet", "sid"],
        "benchmark": ["factsheet", "sid"],
        "statement_download": ["amc_faq", "amc_help"],
        "tax_document": ["amc_faq", "amc_help"]
    },
    "validation": {
        "expense_ratio": r"^[\d.]+%$",
        "nav": r"^Rs\.?\s*[\d.,]+$",
        "min_sip_amount": r"^Rs\.?\s*[\d,]+$"
    }
}

# Relevant fields per problem statement
RELEVANT_FIELDS = {
    "expense_ratio": ["expense ratio", "total expense ratio", "ter"],
    "exit_load": ["exit load", "redemption charge", "contingent deferred sales charge"],
    "min_sip_amount": ["minimum sip", "sip minimum", "min sip", "minimum investment"],
    "lock_in_period": ["lock in", "lock-in", "elss lock", "mandatory lock"],
    "riskometer": ["riskometer", "risk level", "risk grade", "risk profile"],
    "benchmark": ["benchmark", "underlying index", "comparison index"],
    "statement_download": ["statement download", "account statement", "capital gains statement"],
    "tax_document": ["tax certificate", "capital gains tax", "tax statement"],
    "fund_category": ["category", "scheme type", "fund type"],
    "nav": ["nav", "net asset value"],
    "aum": ["aum", "assets under management", "fund size"],
    "fund_manager": ["fund manager", "portfolio manager"],
    "inception_date": ["inception", "launch date", "commencement"]
}

# Advisory patterns to detect and reject
ADVISORY_PATTERNS = [
    r"should\s+i\s+invest",
    r"which\s+fund\s+is\s+better",
    r"which\s+is\s+better",
    r"recommend",
    r"advice",
    r"best\s+fund",
    r"top\s+performing",
    r"highest\s+returns",
    r"compare\s+funds",
    r"better\s+option",
    r"should\s+i\s+buy",
    r"worth\s+investing",
]

# Compliance and Resources
AMFI_RESOURCES = "https://www.amfiindia.com/investor-corner/information-center/mutual-fund-faq"
SEBI_RESOURCES = "https://investor.sebi.gov.in/"
LAST_UPDATED_DATE = "April 14, 2026"

# Document sources
MUTUAL_FUND_URLS = {
    "SBI": {
        "bluechip": "https://kuvera.in/explore/sbi-bluechip-fund--direct-plan--growth-option--SBI072-GR",
        "small_cap": "https://kuvera.in/explore/sbi-small-cap-fund--direct-plan--growth-option--SBI230-GR",
        "contra": "https://kuvera.in/explore/sbi-contra-fund--direct-plan--growth-option--SBI086-GR",
        "large_cap": "https://kuvera.in/explore/sbi-large-cap-fund--direct-plan--growth-option--SBI061-GR",
        "magnum_midcap": "https://kuvera.in/explore/sbi-magnum-midcap-fund--direct-plan--growth-option--SBI146-GR"
    },
    "ICICI": {
        "bluechip": "https://kuvera.in/explore/icici-prudential-bluechip-fund--direct-plan--growth-option--ICICI317-GR",
        "value_discovery": "https://kuvera.in/explore/icici-prudential-value-discovery-fund--direct-plan--growth-option--ICICI343-GR",
        "balanced_advantage": "https://kuvera.in/explore/icici-prudential-balanced-advantage-fund--direct-plan--growth-option--ICICI363-GR",
        "nasdaq_100": "https://kuvera.in/explore/icici-prudential-nasdaq-100-index-fund--direct-plan--growth-option--ICICI840-GR",
        "multicap": "https://kuvera.in/explore/icici-prudential-multicap-fund--direct-plan--growth-option--ICICI333-GR"
    },
    "HDFC": {
        "flexi_cap": "https://kuvera.in/explore/hdfc-flexi-cap-fund--direct-plan--growth-option--INF179K01UT0",
        "balanced_advantage": "https://kuvera.in/explore/hdfc-balanced-advantage-fund--direct-plan--growth-option--HDFC175-GR",
        "mid_cap_opportunities": "https://kuvera.in/explore/hdfc-mid-cap-opportunities-fund--direct-plan--growth-option--HDFC118-GR",
        "top_100": "https://kuvera.in/explore/hdfc-top-100-fund--direct-plan--growth-option--HDFC018-GR",
        "index_nifty_50": "https://kuvera.in/explore/hdfc-index-fund-nifty-50-plan--direct-plan--growth-option--HDFC229-GR"
    },
    "Nippon": {
        "small_cap": "https://kuvera.in/explore/nippon-india-small-cap-fund--direct-plan--growth-option--RN-072-GR",
        "large_cap": "https://kuvera.in/explore/nippon-india-large-cap-fund--direct-plan--growth-option--RN-046-GR",
        "growth_fund": "https://kuvera.in/explore/nippon-india-growth-fund--direct-plan--growth-option--RN-017-GR",
        "multicap": "https://kuvera.in/explore/nippon-india-multi-cap-fund--direct-plan--growth-option--RN-049-GR",
        "pharma": "https://kuvera.in/explore/nippon-india-pharma-fund--direct-plan--growth-option--RN-033-GR"
    },
    "Kotak": {
        "flexicap": "https://kuvera.in/explore/kotak-flexicap-fund--direct-plan--growth-option--KMF-165-GR",
        "small_cap": "https://kuvera.in/explore/kotak-small-cap-fund--direct-plan--growth-option--KMF-078-GR",
        "emerging_equities": "https://kuvera.in/explore/kotak-emerging-equity-fund--direct-plan--growth-option--KMF-069-GR",
        "equity_opportunities": "https://kuvera.in/explore/kotak-equity-opportunities-fund--direct-plan--growth-option--KMF-026-GR",
        "equity_hybrid": "https://kuvera.in/explore/kotak-equity-hybrid-fund--direct-plan--growth-option--KMF-160-GR"
    }
}

