"""Input validation utilities."""
import re
from typing import Optional

from mf_assistant.config import get_settings

settings = get_settings()


def validate_query_length(query: str) -> bool:
    """Validate query length is within limits."""
    return 1 <= len(query) <= settings.MAX_QUERY_LENGTH


def detect_pii(text: str) -> Optional[str]:
    """
    Detect potential PII in text.
    Returns the type of PII detected or None.
    """
    pii_patterns = {
        "PAN": r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
        "AADHAAR": r'\d{4}[\s-]?\d{4}[\s-]?\d{4}',
        "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "PHONE": r'\b\d{10}\b',
        "ACCOUNT_NUMBER": r'\b\d{9,18}\b',
    }
    
    for pii_type, pattern in pii_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return pii_type
    
    return None


def validate_url(url: str, allowed_domains: list) -> bool:
    """Validate URL is from allowed domains."""
    for domain in allowed_domains:
        if domain in url:
            return True
    return False


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def is_advisory_query(query: str) -> bool:
    """
    Check if query is advisory in nature.
    Returns True if advisory patterns are detected.
    """
    from mf_assistant.config import ADVISORY_PATTERNS
    
    query_lower = query.lower()
    
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    
    return False
