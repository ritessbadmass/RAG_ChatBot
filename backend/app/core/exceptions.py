"""Custom exceptions for the application."""


class MutualFundFAQException(Exception):
    """Base exception for the application."""
    pass


class AdvisoryQueryException(MutualFundFAQException):
    """Raised when an advisory query is detected."""
    pass


class PIIDetectedException(MutualFundFAQException):
    """Raised when PII is detected in user input."""
    pass


class DocumentNotFoundException(MutualFundFAQException):
    """Raised when a document is not found."""
    pass


class ScrapingException(MutualFundFAQException):
    """Raised when scraping fails."""
    pass


class VectorStoreException(MutualFundFAQException):
    """Raised when vector store operations fail."""
    pass


class RateLimitException(MutualFundFAQException):
    """Raised when rate limit is exceeded."""
    pass
