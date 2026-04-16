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
        "portal": "https://www.sbimf.com/en-us/offer-document-sid-kim",
        "factsheets": "https://www.sbimf.com/en-us/portfolios",
        "large_cap": "https://www.sbimf.com/en-us/equity-schemes/sbi-large-cap-fund",
        "small_cap": "https://www.sbimf.com/en-us/equity-schemes/sbi-small-cap-fund",
        "contra": "https://www.sbimf.com/en-us/equity-schemes/sbi-contra-fund"
    },
    "ICICI": {
        "portal": "https://www.icicipruamc.com/downloads",
        "factsheets": "https://www.icicipruamc.com/downloads/factsheets",
        "bluechip": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-bluechip-fund",
        "value_discovery": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-value-discovery-fund",
        "balanced_advantage": "https://www.icicipruamc.com/mutual-funds/hybrid-funds/icici-prudential-balanced-advantage-fund"
    },
    "HDFC": {
        "portal": "https://www.hdfcfund.com/investor-desk/product-literature/kim",
        "factsheets": "https://www.hdfcfund.com/investor-desk/product-literature/factsheets",
        "balanced_advantage": "https://www.hdfcfund.com/product-literature/product-literature-details?literature_type=kim&scheme_name=hdfc-balanced-advantage-fund",
        "flexi_cap": "https://www.hdfcfund.com/product-literature/product-literature-details?literature_type=kim&scheme_name=hdfc-flexi-cap-fund",
        "mid_cap_opportunities": "https://www.hdfcfund.com/product-literature/product-literature-details?literature_type=kim&scheme_name=hdfc-mid-cap-opportunities-fund"
    },
    "Nippon": {
        "portal": "https://mf.nipponindiaim.com/investor-services/downloads/forms",
        "factsheets": "https://mf.nipponindiaim.com/investor-services/downloads/factsheets",
        "small_cap": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-small-cap-fund",
        "multi_cap": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-multi-cap-fund",
        "large_cap": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-large-cap-fund"
    },
    "Kotak": {
        "portal": "https://www.kotakmf.com/Information/forms-and-downloads",
        "factsheets": "https://www.kotakmf.com/Information/factsheet",
        "flexicap": "https://www.kotakmf.com/funds/equity-funds/kotak-flexicap-fund",
        "emerging_equities": "https://www.kotakmf.com/funds/equity-funds/kotak-emerging-equity-fund",
        "small_cap": "https://www.kotakmf.com/funds/equity-funds/kotak-small-cap-fund"
    }
}

