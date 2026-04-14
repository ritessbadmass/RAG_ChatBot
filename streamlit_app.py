"""Streamlit UI for Mutual Fund FAQ Assistant - Kuvera-inspired fintech design."""
import streamlit as st
import uuid

# Page configuration
st.set_page_config(
    page_title="MF FAQ Assistant",
    page_icon=":moneybag:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kuvera-inspired fintech styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .header-title {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 8px;
    }
    
    .header-subtitle {
        font-size: 16px;
        color: #64748b;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 32px;
        min-height: 600px;
        box-shadow: 0 10px 40px rgba(92, 89, 232, 0.05);
        border: 1px solid #f1f5f9;
    }
    
    /* Message styling */
    .chat-message {
        padding: 16px 24px;
        margin: 16px 0;
        border-radius: 12px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .user-message {
        background: #5c59e8;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }
    
    .bot-message {
        background: #f8fafc;
        color: #1e293b;
        border-bottom-left-radius: 2px;
    }
    
    /* Source Badge */
    .source-link {
        display: inline-flex;
        align-items: center;
        color: #5c59e8;
        text-decoration: none;
        font-size: 12px;
        font-weight: 600;
        margin-top: 12px;
        padding: 6px 12px;
        background: rgba(92, 89, 232, 0.08);
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .source-link:hover {
        background: rgba(92, 89, 232, 0.15);
        transform: translateY(-1px);
    }
    
    /* Disclaimer */
    .disclaimer {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 32px;
        font-size: 13px;
        color: #92400e;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Quick Actions */
    .quick-action-btn {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 20px;
        font-size: 14px;
        color: #1e293b;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .quick-action-btn:hover {
        border-color: #5c59e8;
        color: #5c59e8;
        background: rgba(92, 89, 232, 0.02);
    }
    
    /* Sidebar */
    .sidebar-content {
        padding: 20px;
    }
    
    .sidebar-title {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 12px;
    }
    
    .sidebar-text {
        font-size: 13px;
        color: #64748b;
        line-height: 1.6;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
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

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1 class="header-title">Mutual Fund FAQ Assistant</h1>
    <p class="header-subtitle">Get factual answers from official AMC documents</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <span class="disclaimer-icon">[!]</span>
    <strong>Facts-only. No investment advice.</strong> This chatbot provides factual information 
    from official AMC documents (Factsheets, SID, KIM) only. Always consult a financial advisor 
    before making investment decisions.
</div>
""", unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">About</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Wholesome RAG-based factual assistant for India\'s leading AMCs.</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">Official Doc Sources</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="sidebar-text">
    - SBI Mutual Fund (Official)<br>
    - ICICI Prudential (Official)<br>
    - HDFC Mutual Fund (Official)<br>
    - Nippon India (Official)<br>
    - Kotak Mahindra (Official)
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">Data Updates</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Daily at 9:15 AM IST via automated pipeline</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start New Chat", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Quick action buttons
st.markdown("<p style='font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 16px;'>Popular Questions</p>", unsafe_allow_html=True)
quick_questions = [
    "What is the expense ratio of SBI Bluechip Fund?",
    "Minimum SIP amount for HDFC Flexi Cap?",
    "How can I download my capital gains statement?"
]
cols = st.columns(len(quick_questions))
for i, question in enumerate(quick_questions):
    if cols[i].button(question, key=f"quick_{i}", use_container_width=True):
        st.session_state.quick_question = question
        st.rerun()

st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <p class="message-text">{message['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        source_url = message.get("source_url", "#")
        source_label = message.get("source", "Official Document")
        st.markdown(f"""
        <div class="chat-message bot-message">
            <p class="message-text">{message['content']}</p>
            <a href="{source_url}" target="_blank" class="source-link">
                <span>[DOC] {source_label}</span>
            </a>
        </div>
        """, unsafe_allow_html=True)

# Chat input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Check for quick question
if "quick_question" in st.session_state:
    prompt = st.session_state.quick_question
    del st.session_state.quick_question
else:
    prompt = st.chat_input("Ask about mutual funds...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    # Display user message
    st.markdown(f"""
    <div class="chat-message user-message">
        <p class="message-text">{prompt}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get bot response with spinner
    with st.spinner(""):
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
                result = rag_service.process_query(
                    query=prompt,
                    thread_history=st.session_state.conversation_history[:-1]
                )
                response_text = result["answer"]
                source = result.get("source", "AMC Official Document")
            
            # Display bot response
            source_url = result.get("source_url", "#") if "source_url" in locals() else "#"
            st.markdown(f"""
            <div class="chat-message bot-message">
                <p class="message-text">{response_text}</p>
                <a href="{source_url}" target="_blank" class="source-link">
                    <span>[DOC] {source}</span>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Add to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "source": source,
                "source_url": source_url
            })
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
        except Exception as e:
            error_msg = "Sorry, I encountered an error. Please try again."
            st.markdown(f"""
            <div class="chat-message bot-message">
                <p class="message-text" style="color: #dc2626;">[ERROR] {error_msg}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown('</div>', unsafe_allow_html=True)  # Close input-container
st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container
st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
    Powered by Groq LLM | Data from official AMC sources | Updated daily at 9:15 AM IST
</div>
""", unsafe_allow_html=True)
