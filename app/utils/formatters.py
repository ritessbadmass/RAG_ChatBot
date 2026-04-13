"""Response formatting utilities."""
from datetime import datetime
from typing import Dict, Any


def format_currency(value: str) -> str:
    """Format currency value."""
    # Remove existing Rs. or INR and standardize
    value = value.replace("Rs.", "").replace("INR", "").replace("Rs", "").strip()
    return f"Rs. {value}"


def format_percentage(value: str) -> str:
    """Format percentage value."""
    # Remove existing % and standardize
    value = value.replace("%", "").strip()
    return f"{value}%"


def truncate_to_three_sentences(text: str) -> str:
    """Truncate text to maximum 3 sentences."""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if len(sentences) <= 3:
        return text
    return '. '.join(sentences[:3]) + '.'


def format_chat_response(
    answer: str,
    source_url: str,
    thread_id: str,
    query_type: str,
    last_updated: str = None
) -> Dict[str, Any]:
    """Format chat response according to requirements."""
    if last_updated is None:
        last_updated = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Ensure answer is max 3 sentences
    formatted_answer = truncate_to_three_sentences(answer)
    
    return {
        "answer": formatted_answer,
        "source_url": source_url,
        "last_updated": last_updated,
        "thread_id": thread_id,
        "query_type": query_type,
        "disclaimer": "Facts-only. No investment advice."
    }


def format_fund_name(amc: str, scheme: str) -> str:
    """Format fund name consistently."""
    return f"{amc} {scheme}".title()


def extract_date_from_string(date_str: str) -> str:
    """Extract and standardize date from string."""
    # Try common date formats
    formats = [
        "%d-%b-%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%b %d, %Y",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Return original if parsing fails
    return date_str
