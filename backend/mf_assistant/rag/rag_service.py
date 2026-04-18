"""RAG (Retrieval-Augmented Generation) Service."""
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from mf_assistant.config import get_settings, LAST_UPDATED_DATE, AMFI_RESOURCES, SEBI_RESOURCES
from mf_assistant.models.schemas import QueryType
from mf_assistant.rag.vector_store import VectorStoreService
from mf_assistant.rag.embedder import EmbeddingService
from mf_assistant.services.query_classifier import QueryClassifier

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """
    Main RAG service that orchestrates:
    1. Query classification
    2. Document retrieval
    3. Context assembly
    4. LLM response generation
    """
    
    # System prompt for factual responses
    SYSTEM_PROMPT = """You are a factual Mutual Fund FAQ Assistant. Your role is to provide accurate, factual information about mutual fund schemes based ONLY on the provided context.

CRITICAL RULES:
1. Answer using ONLY the information in the provided context
2. Maximum 3 sentences per answer
3. Always cite the source URL
4. If information is not in context, say "I don't have that information"
5. NEVER provide investment advice
6. NEVER compare funds or recommend investments
7. Be concise and factual

RESPONSE FORMAT:
- Direct answer (max 3 sentences)
- Source: [URL from context]
"""
    
    ADVISORY_REFUSAL = f"""I cannot provide investment advice. I can only answer factual questions about mutual fund schemes such as:
- Expense ratios
- NAV and AUM
- Exit loads
- Minimum SIP amounts
- Lock-in periods
- Risk levels
- Fund manager details

For educational resources and investment guidance, please visit AMFI: {AMFI_RESOURCES} or SEBI Investor Education: {SEBI_RESOURCES}"""
    
    def __init__(
        self,
        vector_store: Optional[VectorStoreService] = None,
        embedder: Optional[EmbeddingService] = None,
        classifier: Optional[QueryClassifier] = None
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.embedder = embedder or EmbeddingService()
        self.classifier = classifier or QueryClassifier()
        
        # Initialize LLM based on provider
        self.llm = self._initialize_llm()
        
        logger.info(f"Initialized RAG Service with {settings.LLM_PROVIDER} LLM")
    
    def _initialize_llm(self):
        """Initialize LLM based on provider setting."""
        try:
            if settings.LLM_PROVIDER == "groq":
                if not settings.GROQ_API_KEY:
                    logger.warning("GROQ_API_KEY is not set")
                    return None
                    
                from langchain_groq import ChatGroq
                logger.info(f"Using Groq with model: {settings.GROQ_MODEL}")
                return ChatGroq(
                    model=settings.GROQ_MODEL,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0.1,
                    max_tokens=200
                )
            else:
                if not settings.OPENAI_API_KEY:
                    logger.warning("OPENAI_API_KEY is not set")
                    return None

                from langchain_openai import ChatOpenAI
                logger.info(f"Using OpenAI with model: {settings.OPENAI_MODEL}")
                return ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.1,
                    max_tokens=200
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    def process_query(
        self,
        query: str,
        thread_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            query: User query
            thread_history: Optional conversation history
            
        Returns:
            Response dict with answer, source, and metadata
        """
        logger.info(f"Processing query: {query[:50]}...")
        
        # Step 1: Classify query
        query_type, confidence, reason = self.classifier.classify(query)
        logger.info(f"Query classified as {query_type.value} (confidence: {confidence:.2f})")
        
        # Step 2: Handle advisory queries
        if query_type == QueryType.ADVISORY:
            return self._create_refusal_response()
        
        # Step 3: Handle greetings
        if query_type == QueryType.GREETING:
            return self._create_greeting_response()
        
        # Step 4: Retrieve relevant documents
        context, sources = self._retrieve_context(query)
        
        # Step 4.5: Fallback to Seed Data String Search if Vector search failed
        if not context:
            logger.info("Vector search returned no results, trying seed fallback...")
            context, sources = self._fallback_seed_search(query)
        
        if not context:
            return {
                "answer": "I don't have information about that in my knowledge base. Please ask about specific mutual fund schemes.",
                "source_url": "https://www.amfiindia.com/investor-corner/information-center/mutual-fund-faq",
                "query_type": query_type.value,
                "confidence": confidence
            }
        
        # Step 5: Generate response with LLM
        if not self.llm:
            return {
                "answer": "Backend Error: LLM API key not configured. Please add GROQ_API_KEY (or OPENAI_API_KEY) to environment variables.",
                "source_url": "https://dashboard.render.com",
                "query_type": query_type.value,
                "confidence": confidence,
                "sources": sources
            }

        answer = self._generate_response(query, context, thread_history)
        
        # Step 6: Format final response
        return {
            "answer": answer,
            "source_url": sources[0] if sources else "https://www.amfiindia.com",
            "query_type": query_type.value,
            "confidence": confidence,
            "sources": sources
        }
    
    def _retrieve_context(self, query: str, n_results: int = 10) -> tuple:
        """
        Retrieve relevant context from vector store.
        
        Returns:
            Tuple of (context_text, source_urls)
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results
        )
        
        if not results:
            return "", []
        
        # Extract context and sources
        context_parts = []
        sources = set()
        
        for result in results:
            context_parts.append(result['text'])
            if 'source_url' in result['metadata']:
                sources.add(result['metadata']['source_url'])
        
        context = "\n\n".join(context_parts)
        return context, list(sources)
    
    def _fallback_seed_search(self, query: str) -> tuple:
        """Fallback search using direct keyword matching on seed data."""
        try:
            seed_path = Path(__file__).parent.parent / "data" / "seed_data.json"
            if not seed_path.exists():
                return "", []
                
            with open(seed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Simple keyword matching for fund names
            query_lower = query.lower()
            tokens = re.findall(r'\w+', query_lower)
            
            for fund in data.get('funds', []):
                fund_name_lower = fund['fund_name'].lower()
                # If fund name keywords are in query
                if any(word in query_lower for word in fund_name_lower.split()):
                    content = f"""
Fund: {fund['fund_name']}
AMC: {fund['amc']}
Minimum SIP: {fund['min_sip_amount']}
Expense Ratio: {fund['expense_ratio']}
Exit Load: {fund['exit_load']}
Risk Level: {fund['riskometer']}
Category: {fund['category']}
Source: {fund['source_url']}
"""
                    return content.strip(), [fund['source_url']]
            
            return "", []
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return "", []

    def _generate_response(
        self,
        query: str,
        context: str,
        thread_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate response using LLM with context."""
        # Build messages
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
        
        # Add thread history if available
        if thread_history:
            for msg in thread_history[-5:]:  # Last 5 messages for context
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
        
        # Add context and current query
        user_message = f"""Context:
{context}

Question: {query}

Provide a factual answer in maximum 3 sentences."""
        
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        try:
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            # Ensure max 3 sentences
            sentences = [s.strip() for s in answer.split('.') if s.strip()]
            if len(sentences) > 3:
                answer = '. '.join(sentences[:3]) + '.'
            
            # Append compliance footer
            answer = f"{answer}\n\nLast updated from sources: {LAST_UPDATED_DATE}"
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I encountered an error generating the response. Please try again."
    
    def _create_refusal_response(self) -> Dict:
        """Create refusal response for advisory queries."""
        return {
            "answer": f"{self.ADVISORY_REFUSAL}\n\nLast updated from sources: {LAST_UPDATED_DATE}",
            "source_url": AMFI_RESOURCES,
            "query_type": QueryType.ADVISORY.value,
            "confidence": 1.0,
            "is_refusal": True
        }
    
    def _create_greeting_response(self) -> Dict:
        """Create response for greetings."""
        return {
            "answer": "Hello! I'm your Mutual Fund FAQ Assistant. I can answer factual questions about mutual fund schemes like expense ratios, NAV, exit loads, and more. What would you like to know?",
            "source_url": "https://www.amfiindia.com/investor-corner/information-center/mutual-fund-faq",
            "query_type": QueryType.GREETING.value,
            "confidence": 1.0
        }
    
    def get_vector_store_stats(self) -> Dict:
        """Get vector store statistics."""
        return self.vector_store.get_stats()


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
