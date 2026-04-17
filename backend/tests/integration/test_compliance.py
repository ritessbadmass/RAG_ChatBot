"""Compliance tests per problem statement requirements."""
import pytest

from mf_assistant.services.query_classifier import QueryClassifier
from mf_assistant.utils.validators import detect_pii, validate_query_length


class TestProblemStatementCompliance:
    """
    Test compliance with problem statement requirements.
    
    Requirements from problemstatement.md:
    1. Facts-only Q&A (no advisory)
    2. Max 3 sentences per answer
    3. Source URL + last updated
    4. Max 500 chars query
    5. PII detection
    6. Advisory query refusal
    """
    
    @pytest.fixture
    def classifier(self):
        return QueryClassifier()
    
    # Requirement 1: Facts-only, no advisory
    def test_no_advisory_content(self, classifier):
        """Test that advisory queries are rejected."""
        advisory_queries = [
            "Should I invest in mutual funds?",
            "Which fund is better for me?",
            "Can you recommend a good fund?",
            "What is the best performing fund?",
            "Compare SBI and HDFC funds",
            "Is it worth investing in small cap?",
        ]
        
        for query in advisory_queries:
            result = classifier.classify(query)
            assert result[0].value == "advisory", f"Should reject advisory: {query}"
    
    # Requirement 2: Max 3 sentences (tested in response formatting)
    def test_answer_length_constraint(self):
        """Test that answers are limited to 3 sentences."""
        from mf_assistant.utils.formatters import truncate_to_three_sentences
        
        long_answer = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
        truncated = truncate_to_three_sentences(long_answer)
        
        sentences = [s.strip() for s in truncated.split('.') if s.strip()]
        assert len(sentences) <= 3
    
    # Requirement 4: Max 500 chars query
    def test_query_length_limit(self):
        """Test query length validation."""
        assert validate_query_length("Short query") is True
        assert validate_query_length("a" * 500) is True
        assert validate_query_length("a" * 501) is False
        assert validate_query_length("") is False
    
    # Requirement 5: PII detection
    def test_pii_detection(self):
        """Test PII detection."""
        pii_cases = [
            ("My PAN is ABCDE1234F", "PAN"),
            ("Aadhaar 1234 5678 9012", "AADHAAR"),
            ("Email me at test@example.com", "EMAIL"),
            ("Call 9876543210", "PHONE"),
        ]
        
        for query, expected_type in pii_cases:
            detected = detect_pii(query)
            assert detected == expected_type, f"Should detect {expected_type} in: {query}"
    
    def test_no_pii_in_clean_queries(self):
        """Test that clean queries pass PII check."""
        clean_queries = [
            "What is the expense ratio of SBI Blue Chip?",
            "Tell me about HDFC Small Cap Fund",
            "What is the NAV today?",
        ]
        
        for query in clean_queries:
            assert detect_pii(query) is None, f"Should not detect PII in: {query}"
    
    # Requirement 6: Advisory refusal
    def test_advisory_refusal_message(self, classifier):
        """Test that advisory queries get refusal message."""
        query = "Should I invest in SBI Blue Chip Fund?"
        result = classifier.classify(query)
        
        assert result[0].value == "advisory"
        assert result[1] > 0.6  # Confidence > 60%
    
    # Additional: Factual queries accepted
    def test_factual_queries_accepted(self, classifier):
        """Test that factual queries are accepted."""
        factual_queries = [
            "What is the expense ratio?",
            "What is the exit load?",
            "What is the minimum SIP amount?",
            "What is the lock-in period?",
            "What is the riskometer?",
            "What is the benchmark?",
        ]
        
        for query in factual_queries:
            result = classifier.classify(query)
            assert result[0].value == "factual", f"Should accept factual: {query}"


class TestResponseFormatCompliance:
    """Test response format compliance."""
    
    def test_response_has_required_fields(self):
        """Test that response has all required fields."""
        from mf_assistant.models.schemas import ChatResponse
        from datetime import datetime
        
        response = ChatResponse(
            answer="This is the answer.",
            source_url="https://example.com",
            last_updated=datetime.now().strftime("%Y-%m-%d"),
            thread_id="test-thread",
            query_type="factual"
        )
        
        assert response.answer is not None
        assert response.source_url is not None
        assert response.last_updated is not None
        assert response.thread_id is not None
        assert response.query_type is not None
        assert response.disclaimer is not None
