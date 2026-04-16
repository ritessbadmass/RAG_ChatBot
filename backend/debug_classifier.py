import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(os.getcwd())))

from mf_assistant.services.query_classifier import QueryClassifier
from mf_assistant.models.schemas import QueryType

def debug():
    classifier = QueryClassifier()
    
    # Factual check
    query = "What is the expense ratio of SBI Blue Chip Fund?"
    query_type, confidence, reason = classifier.classify(query)
    print(f"Query: {query}")
    print(f"Type: {query_type}")
    print(f"Match: {query_type == QueryType.FACTUAL}")
    
    # Advisory check
    query2 = "Should I invest in SBI Blue Chip Fund?"
    query_type2, confidence2, reason2 = classifier.classify(query2)
    print(f"\nQuery: {query2}")
    print(f"Type: {query_type2}")
    print(f"Confidence: {confidence2}")
    print(f"Match: {query_type2 == QueryType.ADVISORY}")

if __name__ == '__main__':
    debug()
