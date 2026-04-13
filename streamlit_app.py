"""Streamlit UI for Mutual Fund FAQ Assistant."""
import streamlit as st
import requests
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for fintech styling
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    .stChatMessage.user {
        background-color: #e0f2fe;
        border-left: 4px solid #0284c7;
    }
    .stChatMessage.assistant {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
    }
    .disclaimer {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 20px;
        font-size: 14px;
        color: #92400e;
    }
    .source-badge {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 8px;
        display: inline-block;
    }
    .stTextInput > div > div > input {
        border-radius: 24px;
        border: 2px solid #e2e8f0;
        padding: 12px 20px;
    }
    .stButton > button {
        border-radius: 24px;
        background-color: #0284c7;
        color: white;
        padding: 12px 24px;
        font-weight: 600;
    }
    h1 {
        color: #0f172a;
        font-weight: 700;
    }
    .subtitle {
        color: #64748b;
        font-size: 16px;
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Header
st.markdown("<h1>📊 Mutual Fund FAQ Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Get factual answers about mutual fund schemes</p>", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Disclaimer:</strong> Facts-only. No investment advice. 
    This chatbot provides factual information from official AMC documents only.
</div>
""", unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.write("""
    This assistant answers factual questions about 25 mutual fund schemes 
    from 5 major AMCs:
    - SBI Mutual Fund
    - ICICI Prudential
    - HDFC Mutual Fund
    - Nippon India
    - Kotak Mahindra
    
    **Data updated daily at 9:15 AM IST**
    """)
    
    st.header("Example Questions")
    st.write("""
    - What is the expense ratio of SBI Blue Chip Fund?
    - Tell me about ICICI Prudential Technology Fund
    - What are the top holdings of HDFC Mid-Cap Opportunities?
    - Explain the investment objective of Nippon India Small Cap
    """)
    
    if st.button("🔄 New Conversation"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "source" in message:
            st.markdown(f"<span class='source-badge'>📄 {message['source']}</span>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about mutual funds..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Searching official documents..."):
            try:
                # Call RAG service directly
                from app.rag.rag_service import RAGService
                from app.services.query_classifier import QueryClassifier
                
                rag_service = RAGService()
                classifier = QueryClassifier()
                
                # Classify query
                classification = classifier.classify(prompt)
                
                if classification["is_advisory"]:
                    response_text = "I cannot provide investment advice. I can only share factual information from official AMC documents."
                    source = "System"
                elif classification["is_procedural"]:
                    response_text = "For account-related queries, please contact the respective AMC directly or visit their official website."
                    source = "System"
                else:
                    # Get answer from RAG
                    result = rag_service.query(
                        query=prompt,
                        thread_id=st.session_state.thread_id,
                        conversation_history=st.session_state.conversation_history[:-1]
                    )
                    response_text = result["answer"]
                    source = result.get("source", "AMC Official Document")
                
                # Display response
                st.write(response_text)
                st.markdown(f"<span class='source-badge'>📄 {source}</span>", unsafe_allow_html=True)
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "source": source
                })
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                
            except Exception as e:
                error_msg = "Sorry, I encountered an error. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 12px;'>Powered by Groq LLM • Data from official AMC sources</p>", unsafe_allow_html=True)
