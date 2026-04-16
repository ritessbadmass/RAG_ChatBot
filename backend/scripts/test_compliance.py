import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mf_assistant.rag.rag_service import RAGService
from mf_assistant.models.schemas import QueryType

def test_compliance():
    """Verify chatbot compliance logic."""
    print("Starting Compliance Tests...")
    print("=" * 50)
    
    rag = RAGService()
    
    # Mock result with long answer to test sentence trimming
    mock_long_answer = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    
    # Test 1: Sentence Trimming
    print("\nTest 1: Sentence Trimming")
    # messages = [{"role": "system", "content": "dummy"}]
    
    # Test 2: Advisory Refusal
    print("\nTest 2: Advisory Refusal")
    advisory_query = "Should I invest in SBI Bluechip Fund?"
    result = rag.process_query(advisory_query)
    
    answer = result["answer"]
    print(f"Query: {advisory_query}")
    print(f"Response snippet: {answer[:100]}...")
    
    assert "cannot provide investment advice" in answer
    assert "AMFI" in answer or "SEBI" in answer
    assert "Last updated from sources:" in answer
    print("Advisory Refusal Passed!")
    
    # Test 3: Formatting (Factual Query)
    print("\nTest 3: Factual Query (Check Footer)")
    factual_query = "What is the expense ratio?"
    result = rag.process_query(factual_query)
    
    answer = result["answer"]
    print(f"Query: {factual_query}")
    print(f"Response footer check: {'Last updated' in answer}")
    
    assert "Last updated from sources:" in answer
    print("Factual Footer Passed!")

if __name__ == "__main__":
    try:
        test_compliance()
    except Exception as e:
        print(f"Test failed: {e}")
