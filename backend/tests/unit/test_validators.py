"""Unit tests for validators."""
import pytest

from mf_assistant.utils.validators import (
    detect_pii,
    validate_query_length,
    is_advisory_query,
    sanitize_input,
)
from mf_assistant.config import get_settings


class TestPIIDetection:
    """Test PII detection."""
    
    def test_detect_pan(self):
        """Test PAN number detection."""
        assert detect_pii("My PAN is ABCDE1234F") == "PAN"
        assert detect_pii("PAN: ABCDE1234F") == "PAN"
    
    def test_detect_aadhaar(self):
        """Test Aadhaar detection."""
        assert detect_pii("Aadhaar: 1234 5678 9012") == "AADHAAR"
        assert detect_pii("1234-5678-9012") == "AADHAAR"
    
    def test_detect_email(self):
        """Test email detection."""
        assert detect_pii("Contact me at user@example.com") == "EMAIL"
        assert detect_pii("Email: test.user@domain.co.in") == "EMAIL"
    
    def test_detect_phone(self):
        """Test phone number detection."""
        assert detect_pii("Call me at 9876543210") == "PHONE"
        assert detect_pii("My number is 9876543210") == "PHONE"
    
    def test_no_pii(self):
        """Test that clean queries return None."""
        assert detect_pii("What is the expense ratio?") is None
        assert detect_pii("Tell me about SBI Blue Chip Fund") is None


class TestQueryValidation:
    """Test query validation."""
    
    def test_validate_query_length_valid(self):
        """Test valid query lengths."""
        settings = get_settings()
        assert validate_query_length("Short query") is True
        assert validate_query_length("a" * settings.MAX_QUERY_LENGTH) is True
    
    def test_validate_query_length_invalid(self):
        """Test invalid query lengths."""
        settings = get_settings()
        assert validate_query_length("") is False
        assert validate_query_length("a" * (settings.MAX_QUERY_LENGTH + 1)) is False
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        assert sanitize_input("  hello world  ") == "hello world"
        assert sanitize_input("hello   world") == "hello world"


class TestAdvisoryDetection:
    """Test advisory query detection."""
    
    def test_advisory_patterns(self):
        """Test advisory pattern detection."""
        assert is_advisory_query("Should I invest?") is True
        assert is_advisory_query("Which fund is better?") is True
        assert is_advisory_query("Recommend a fund") is True
        assert is_advisory_query("Best performing fund") is True
    
    def test_non_advisory_patterns(self):
        """Test non-advisory queries."""
        assert is_advisory_query("What is the NAV?") is False
        assert is_advisory_query("Expense ratio please") is False
        assert is_advisory_query("Tell me about the fund") is False
