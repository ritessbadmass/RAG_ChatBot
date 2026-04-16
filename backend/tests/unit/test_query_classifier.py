"""Unit tests for query classifier."""
import pytest

from mf_assistant.models.schemas import QueryType
from mf_assistant.services.query_classifier import QueryClassifier


class TestQueryClassifier:
    """Test query classification."""
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return QueryClassifier()
    
    def test_classify_factual_queries(self, classifier, sample_factual_queries):
        """Test that factual queries are correctly classified."""
        for query in sample_factual_queries:
            query_type, confidence, reason = classifier.classify(query)
            assert query_type == QueryType.FACTUAL, f"Failed for: {query}"
            assert confidence > 0.5
            print(f"✓ {query[:50]}... -> {query_type.value} ({confidence:.2f})")
    
    def test_classify_advisory_queries(self, classifier, sample_advisory_queries):
        """Test that advisory queries are correctly classified."""
        for query in sample_advisory_queries:
            query_type, confidence, reason = classifier.classify(query)
            assert query_type == QueryType.ADVISORY, f"Failed for: {query}. Type: {type(query_type)} vs Expected: {type(QueryType.ADVISORY)}. Value: {query_type} vs Expected: {QueryType.ADVISORY}"
            assert confidence > 0.6
            print(f"✓ {query[:50]}... -> {query_type.value} ({confidence:.2f})")
    
    def test_classify_procedural_queries(self, classifier, sample_procedural_queries):
        """Test that procedural queries are correctly classified."""
        for query in sample_procedural_queries:
            query_type, confidence, reason = classifier.classify(query)
            assert query_type == QueryType.PROCEDURAL, f"Failed for: {query}"
            assert confidence > 0.5
            print(f"✓ {query[:50]}... -> {query_type.value} ({confidence:.2f})")
    
    def test_classify_greetings(self, classifier):
        """Test greeting classification."""
        greetings = ["hi", "hello", "thanks", "thank you", "bye"]
        for greeting in greetings:
            query_type, confidence, _ = classifier.classify(greeting)
            assert query_type == QueryType.GREETING
            assert confidence > 0.9
    
    def test_is_advisory(self, classifier, sample_advisory_queries):
        """Test advisory detection helper."""
        for query in sample_advisory_queries:
            assert classifier.is_advisory(query), f"Should be advisory: {query}"
    
    def test_is_not_advisory(self, classifier, sample_factual_queries):
        """Test that factual queries are not flagged as advisory."""
        for query in sample_factual_queries:
            assert not classifier.is_advisory(query), f"Should not be advisory: {query}"
    
    def test_get_query_intent(self, classifier):
        """Test intent extraction."""
        query = "What is the expense ratio of SBI Blue Chip?"
        intent = classifier.get_query_intent(query)
        
        assert intent["query_type"] == QueryType.FACTUAL.value
        assert intent["can_answer"] is True
        assert "expense_ratio" in intent["mentioned_fields"]
    
    def test_extract_mentioned_fields(self, classifier):
        """Test field extraction."""
        query = "What is the NAV and expense ratio?"
        fields = classifier._extract_mentioned_fields(query)
        
        assert "nav" in fields
        assert "expense_ratio" in fields


class TestComplianceRequirements:
    """Test compliance with problem statement requirements."""
    
    @pytest.fixture
    def classifier(self):
        return QueryClassifier()
    
    def test_advisory_rejection_patterns(self, classifier):
        """Test specific advisory patterns from problem statement."""
        advisory_examples = [
            "Should I invest in this fund?",
            "Which fund is better for me?",
            "Can you recommend a fund?",
            "What are the best performing funds?",
            "Compare these two funds",
        ]
        
        for query in advisory_examples:
            query_type, confidence, _ = classifier.classify(query)
            assert query_type == QueryType.ADVISORY, f"Should reject: {query}"
            assert confidence >= 0.6, f"Confidence too low for: {query}"
    
    def test_factual_acceptance(self, classifier):
        """Test that factual queries are accepted."""
        factual_examples = [
            "What is the expense ratio?",
            "What is the exit load?",
            "What is the minimum SIP?",
            "What is the lock-in period?",
            "What is the riskometer?",
        ]
        
        for query in factual_examples:
            query_type, confidence, _ = classifier.classify(query)
            assert query_type == QueryType.FACTUAL, f"Should accept: {query}"
            assert confidence >= 0.5
