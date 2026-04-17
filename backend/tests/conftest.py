"""Pytest configuration and fixtures."""
import sys
import os

# Add the parent directory to Python path so 'app' can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from mf_assistant.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_factual_queries():
    """Sample factual queries for testing."""
    return [
        "What is the expense ratio of SBI Blue Chip Fund?",
        "What is the NAV of HDFC Small Cap Fund?",
        "What is the exit load for ICICI Prudential Balanced Advantage?",
        "What is the minimum SIP amount for Nippon India Small Cap?",
        "What is the lock-in period for Kotak ELSS?",
        "What is the riskometer rating of SBI Equity Hybrid?",
        "Who is the fund manager of HDFC Mid Cap Opportunities?",
    ]


@pytest.fixture
def sample_advisory_queries():
    """Sample advisory queries that should be rejected."""
    return [
        "Should I invest in SBI Blue Chip Fund?",
        "Which fund is better: HDFC or ICICI?",
        "Can you recommend a good mutual fund?",
        "What is the best performing fund right now?",
        "Compare SBI Small Cap and Nippon Small Cap",
        "Is it worth investing in Kotak Emerging Equity?",
        "Which fund will give highest returns?",
    ]


@pytest.fixture
def sample_pii_queries():
    """Sample queries containing PII."""
    return [
        "My PAN is ABCDE1234F and I want to know about...",
        "My Aadhaar 1234 5678 9012 is linked to...",
        "Contact me at user@example.com for details",
        "My phone number 9876543210 is registered",
    ]


@pytest.fixture
def sample_procedural_queries():
    """Sample procedural queries."""
    return [
        "How do I download my account statement?",
        "Where can I get my capital gains statement?",
        "How to download tax certificate?",
    ]
