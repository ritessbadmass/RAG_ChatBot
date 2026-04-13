"""Streamlit UI for Mutual Fund FAQ Assistant - Kuvera-inspired fintech design."""
import streamlit as st
import uuid

# Page configuration
st.set_page_config(
    page_title="MF FAQ Assistant",
    page_icon="💰",
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
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header styling */
    .header {
        background: white;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        min-height: 500px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Message styling */
    .chat-message {
        padding: 16px 20px;
        margin: 12px 0;
        border-radius: 12px;
        max-width: 85%;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .bot-message {
        background: #f8fafc;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-bottom-left-radius: 4px;
    }
    
    .message-text {
        font-size: 15px;
        line-height: 1.6;
        margin: 0;
    }
    
    .message-time {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 8px;
    }
    
    /* Source badge */
    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #dbeafe;
        color: #1e40af;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
        margin-top: 12px;
    }
    
    /* Input area */
    .input-container {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Disclaimer */
    .disclaimer {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        font-size: 13px;
        color: #92400e;
    }
    
    .disclaimer-icon {
        font-size: 16px;
        margin-right: 8px;
    }
    
    /* Quick actions */
    .quick-actions {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin: 16px 0;
    }
    
    .quick-action-btn {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        color: #475569;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .quick-action-btn:hover {
        background: #e2e8f0;
        border-color: #cbd5e1;
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
    <h1 class="header-title">💰 Mutual Fund FAQ Assistant</h1>
    <p class="header-subtitle">Get factual answers from official AMC documents</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <span class="disclaimer-icon">⚠️</span>
    <strong>Facts-only. No investment advice.</strong> This chatbot provides factual information 
    from official AMC documents (Factsheets, SID, KIM) only. Always consult a financial advisor 
    before making investment decisions.
</div>
""", unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">📊 About</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="sidebar-text">
    This assistant answers factual questions about <strong>25 mutual fund schemes</strong> 
    from 5 major AMCs using official documents (Factsheets, SID, KIM).
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">🏦 Supported AMCs</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="sidebar-text">
    • SBI Mutual Fund<br>
    • ICICI Prudential<br>
    • HDFC Mutual Fund<br>
    • Nippon India<br>
    • Kotak Mahindra
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">⏰ Data Updates</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Daily at 9:15 AM IST via automated pipeline</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Quick action buttons
st.markdown("<p style='font-size: 13px; color: #64748b; margin-bottom: 12px;'>💡 Try asking:</p>", unsafe_allow_html=True)
quick_questions = [
    "What is expense ratio?",
    "SBI Blue Chip Fund details",
    "ICICI Technology Fund holdings",
    "Compare large cap funds"
]
cols = st.columns(4)
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
        source_html = f"<div class='source-badge'>📄 {message['source']}</div>" if "source" in message else ""
        st.markdown(f"""
        <div class="chat-message bot-message">
            <p class="message-text">{message['content']}</p>
            {source_html}
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
                result = rag_service.query(
                    query=prompt,
                    thread_id=st.session_state.thread_id,
                    conversation_history=st.session_state.conversation_history[:-1]
                )
                response_text = result["answer"]
                source = result.get("source", "AMC Official Document")
            
            # Display bot response
            st.markdown(f"""
            <div class="chat-message bot-message">
                <p class="message-text">{response_text}</p>
                <div class='source-badge'>📄 {source}</div>
            </div>
            """, unsafe_allow_html=True)
            
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
            st.markdown(f"""
            <div class="chat-message bot-message">
                <p class="message-text" style="color: #dc2626;">⚠️ {error_msg}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown('</div>', unsafe_allow_html=True)  # Close input-container
st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container
st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
    Powered by Groq LLM • Data from official AMC sources • Updated daily at 9:15 AM IST
</div>
""", unsafe_allow_html=True)
