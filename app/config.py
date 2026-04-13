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
    GROQ_MODEL: str = "llama3-8b-8192"
    
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
        "nipponindiamf.com",
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

# Document sources
MUTUAL_FUND_URLS = {
    "SBI": {
        "equity_hybrid": "https://kuvera.in/mutual-funds/fund/sbi-equity-hybrid-growth--SBD24G-GR",
        "large_cap": "https://kuvera.in/mutual-funds/fund/sbi-large-cap-growth--SBD103G-GR",
        "contra": "https://kuvera.in/mutual-funds/fund/sbi-contra-growth--SBD036G-GR",
        "small_cap": "https://kuvera.in/mutual-funds/fund/sbi-small-cap-growth--SBD346G-GR",
        "nifty_50_etf": "https://kuvera.in/stocks/sbi-nifty-50-etf"
    },
    "ICICI": {
        "bluechip": "https://kuvera.in/mutual-funds/fund/icici-prudential-bluechip-growth--8042-GR",
        "value_discovery": "https://kuvera.in/mutual-funds/fund/icici-prudential-value-discovery-growth--8176-GR",
        "balanced_advantage": "https://kuvera.in/mutual-funds/fund/icici-prudential-balanced-advantage-growth--8180-GR",
        "multi_asset": "https://kuvera.in/mutual-funds/fund/icici-prudential-multi-asset-growth--8004-GR",
        "equity_debt": "https://kuvera.in/mutual-funds/fund/icici-prudential-equity-debt-growth--8017-GR"
    },
    "HDFC": {
        "balanced_advantage": "https://kuvera.in/mutual-funds/fund/hdfc-balanced-advantage-growth--GFGT-GR",
        "flexi_cap": "https://kuvera.in/mutual-funds/fund/hdfc-flexicap-growth--02T-GR",
        "mid_cap_opportunities": "https://kuvera.in/mutual-funds/fund/hdfc-mid-cap-opportunities-growth--MCOGT-GR",
        "small_cap": "https://kuvera.in/mutual-funds/fund/hdfc-small-cap-growth--HDACG1G-GR",
        "large_cap": "https://kuvera.in/mutual-funds/fund/hdfc-large-cap-growth--44T-GR"
    },
    "Nippon": {
        "small_cap": "https://kuvera.in/mutual-funds/fund/nippon-india-small-cap-growth--SCAG-GR",
        "nifty_50_bees": "https://kuvera.in/stocks/nippon-india-etf-nifty-50-bees",
        "multi_cap": "https://kuvera.in/mutual-funds/fund/nippon-india-multi-cap-growth--EOAG-GR",
        "growth_fund": "https://kuvera.in/mutual-funds/fund/nippon-india-growth-fund-growth--GFAG-GR",
        "large_cap": "https://kuvera.in/mutual-funds/fund/nippon-india-large-cap-growth--EAAG-GR"
    },
    "Kotak": {
        "equity_arbitrage": "https://kuvera.in/mutual-funds/fund/kotak-equity-arbitrage-growth--KO179D-GR",
        "midcap": "https://kuvera.in/mutual-funds/fund/kotak-emerging-equity-growth--KO123D-GR",
        "flexicap": "https://kuvera.in/mutual-funds/fund/kotak-flexicap-growth--KO168D-GR",
        "emerging_equities": "https://kuvera.in/mutual-funds/fund/kotak-emerging-equity-growth--KO123D-GR",
        "small_cap": "https://kuvera.in/mutual-funds/fund/kotak-small-cap-growth--KO104D-GR"
    }
}
