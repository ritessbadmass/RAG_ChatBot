"""Query classification service for detecting query types."""
import logging
import re
from typing import Dict, List, Optional, Tuple

from app.config import ADVISORY_PATTERNS, RELEVANT_FIELDS
from app.models.schemas import QueryType

logger = logging.getLogger(__name__)


class QueryClassifier:
    """
    Classifies user queries into different types:
    - FACTUAL: Questions about fund facts (expense ratio, NAV, etc.)
    - ADVISORY: Investment advice requests (will be rejected)
    - PROCEDURAL: How-to questions (download statements, etc.)
    - GREETING: Hello, thanks, etc.
    - UNKNOWN: Uncategorized
    """
    
    # Greeting patterns
    GREETING_PATTERNS = [
        r'^\s*(hi|hello|hey|greetings)\s*$',
        r'^\s*(thanks?|thank you|ty)\s*$',
        r'^\s*(bye|goodbye|see you)\s*$',
        r'^\s*(ok|okay|got it)\s*$',
    ]
    
    # Procedural patterns
    PROCEDURAL_PATTERNS = [
        r'how\s+(?:do|can|to)\s+i\s+(?:download|get|access)',
        r'where\s+(?:can|do)\s+i\s+(?:find|get|download)',
        r'how\s+to\s+(?:download|access|view)',
        r'statement\s+download',
        r'tax\s+certificate',
        r'capital\s+gains\s+statement',
    ]
    
    # Factual patterns (mutual fund specific)
    FACTUAL_PATTERNS = [
        r'what\s+is\s+(?:the\s+)?(?:expense\s+ratio|nav|aum|exit\s+load)',
        r'(?:expense\s+ratio|nav|aum|exit\s+load)\s+of',
        r'(?:minimum|min)\s+sip',
        r'lock[-\s]?in\s+period',
        r'riskometer|risk\s+level',
        r'benchmark',
        r'fund\s+manager',
        r'inception\s+date',
    ]
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.greeting_patterns = [re.compile(p, re.IGNORECASE) for p in self.GREETING_PATTERNS]
        self.procedural_patterns = [re.compile(p, re.IGNORECASE) for p in self.PROCEDURAL_PATTERNS]
        self.factual_patterns = [re.compile(p, re.IGNORECASE) for p in self.FACTUAL_PATTERNS]
        self.advisory_patterns = [re.compile(p, re.IGNORECASE) for p in ADVISORY_PATTERNS]
    
    def classify(self, query: str) -> Tuple[QueryType, float, Optional[str]]:
        """
        Classify a query and return type with confidence score.
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (query_type, confidence_score, reason)
        """
        query_lower = query.lower().strip()
        
        # Check for greetings first (highest priority for short queries)
        if len(query_lower) < 20:
            for pattern in self.greeting_patterns:
                if pattern.match(query_lower):
                    return QueryType.GREETING, 0.95, "Greeting detected"
        
        # Check for advisory (highest priority for rejection)
        advisory_score = self._calculate_advisory_score(query_lower)
        if advisory_score > 0.7:
            return QueryType.ADVISORY, advisory_score, "Advisory pattern detected"
        
        # Check for procedural
        procedural_score = self._calculate_procedural_score(query_lower)
        if procedural_score > 0.6:
            return QueryType.PROCEDURAL, procedural_score, "Procedural query detected"
        
        # Check for factual
        factual_score = self._calculate_factual_score(query_lower)
        if factual_score > 0.5:
            return QueryType.FACTUAL, factual_score, "Factual query detected"
        
        # Default to unknown with low confidence
        return QueryType.UNKNOWN, 0.3, "Could not classify query"
    
    def _calculate_advisory_score(self, query: str) -> float:
        """Calculate advisory probability score (0-1)."""
        matches = 0
        for pattern in self.advisory_patterns:
            if pattern.search(query):
                matches += 1
        
        # Score based on number of matches
        if matches == 0:
            return 0.0
        elif matches == 1:
            return 0.8
        elif matches >= 2:
            return 0.9
        return 0.0
    
    def _calculate_procedural_score(self, query: str) -> float:
        """Calculate procedural probability score (0-1)."""
        for pattern in self.procedural_patterns:
            if pattern.search(query):
                return 0.8
        return 0.0
    
    def _calculate_factual_score(self, query: str) -> float:
        """Calculate factual probability score (0-1)."""
        score = 0.0
        
        # Check for factual patterns
        for pattern in self.factual_patterns:
            if pattern.search(query):
                score += 0.3
        
        # Check for relevant field keywords
        for field, keywords in RELEVANT_FIELDS.items():
            for keyword in keywords:
                if keyword in query:
                    score += 0.1
                    break  # Only count once per field
        
        return min(score, 1.0)
    
    def is_advisory(self, query: str) -> bool:
        """Quick check if query is advisory."""
        query_type, confidence, _ = self.classify(query)
        return query_type == QueryType.ADVISORY and confidence > 0.7
    
    def get_query_intent(self, query: str) -> Dict:
        """Get detailed intent analysis."""
        query_type, confidence, reason = self.classify(query)
        
        # Extract mentioned funds/schemes
        mentioned_fields = self._extract_mentioned_fields(query)
        
        return {
            "query_type": query_type.value,
            "confidence": confidence,
            "reason": reason,
            "mentioned_fields": mentioned_fields,
            "can_answer": query_type in [QueryType.FACTUAL, QueryType.PROCEDURAL, QueryType.GREETING]
        }
    
    def _extract_mentioned_fields(self, query: str) -> List[str]:
        """Extract which factual fields are mentioned in query."""
        mentioned = []
        query_lower = query.lower()
        
        for field, keywords in RELEVANT_FIELDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    mentioned.append(field)
                    break
        
        return mentioned


# Singleton instance
_classifier: Optional[QueryClassifier] = None


def get_classifier() -> QueryClassifier:
    """Get or create query classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = QueryClassifier()
    return _classifier
