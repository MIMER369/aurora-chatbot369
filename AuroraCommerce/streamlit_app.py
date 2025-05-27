import streamlit as st
import json
import time
import requests
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="AURORA - E-Commerce AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Matrix theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, rgba(5, 15, 10, 0.97), rgba(0, 5, 0, 0.98));
        color: #ccffcc;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, rgba(0, 40, 0, 0.9), rgba(0, 80, 40, 0.85), rgba(0, 180, 80, 0.8));
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 255, 65, 0.3);
    }
    
    .aurora-logo {
        font-size: 3rem;
        font-weight: bold;
        color: white;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.7);
        margin-bottom: 10px;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #ccffcc;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .chat-message {
        padding: 15px;
        margin: 10px 0;
        border-radius: 15px;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        background: linear-gradient(135deg, #08773d, #00ff41);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .bot-message {
        background: rgba(0, 40, 10, 0.6);
        color: #ccffcc;
        margin-right: 20%;
        border-left: 3px solid #0d7e1e;
        border-bottom-left-radius: 5px;
    }
    
    .source-badge {
        background: linear-gradient(135deg, #00ff41, #0d7e1e);
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        margin-top: 5px;
        display: inline-block;
    }
    
    .category-button {
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid rgba(0, 255, 65, 0.3);
        color: #ccffcc;
        padding: 8px 15px;
        margin: 5px;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .category-button:hover {
        background: linear-gradient(135deg, #00ff41, #0d7e1e);
        color: white;
        transform: translateY(-2px);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.7);
        color: #00ff41;
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-radius: 20px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00ff41, #0d7e1e);
        color: white;
        border: none;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello, I'm AURORA, your personal e-commerce assistant. How may I help you today? Ask me anything about products, shipping, returns, payments, or your account.",
        "source": "welcome"
    })

if 'chatbot' not in st.session_state:
    # Initialize chatbot (import locally to avoid issues)
    try:
        from chatbot import AuroraChatbot
        st.session_state.chatbot = AuroraChatbot()
    except Exception as e:
        st.error(f"Error loading chatbot: {e}")
        st.session_state.chatbot = None

# Header
st.markdown("""
<div class="main-header">
    <div class="aurora-logo">AURORA</div>
    <div class="subtitle">YOUR E-COMMERCE AI ASSISTANT</div>
</div>
""", unsafe_allow_html=True)

# Sidebar with category buttons
with st.sidebar:
    st.markdown("### Quick Categories")
    
    if st.session_state.chatbot:
        categories = st.session_state.chatbot.get_categories()
        
        for category in categories:
            if st.button(f"📂 {category}", key=f"cat_{category}"):
                # Get questions for this category
                questions = st.session_state.chatbot.get_category_questions(category)
                if questions:
                    st.session_state.selected_category = category
                    st.session_state.category_questions = questions[:10]  # Show top 10

# Display category questions if selected
if 'selected_category' in st.session_state and 'category_questions' in st.session_state:
    st.markdown(f"### Questions about {st.session_state.selected_category}")
    
    cols = st.columns(2)
    for i, question in enumerate(st.session_state.category_questions):
        col = cols[i % 2]
        with col:
            if st.button(question[:50] + "..." if len(question) > 50 else question, 
                        key=f"q_{i}", help=question):
                # Add user message
                st.session_state.messages.append({
                    "role": "user", 
                    "content": question
                })
                
                # Get bot response
                if st.session_state.chatbot:
                    response_data = st.session_state.chatbot.get_response(question)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_data.get('response', 'Sorry, I could not find an answer.'),
                        "source": response_data.get('source', 'unknown'),
                        "confidence": response_data.get('confidence', 0.0)
                    })
                
                # Clear category selection
                if 'selected_category' in st.session_state:
                    del st.session_state.selected_category
                if 'category_questions' in st.session_state:
                    del st.session_state.category_questions
                
                st.rerun()

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            confidence_info = ""
            if "confidence" in message and message["confidence"] > 0:
                confidence_info = f" (Confidence: {message['confidence']:.2f})"
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>AURORA:</strong> {message["content"]}
                <div class="source-badge">{message.get('source', 'aurora')}{confidence_info}</div>
            </div>
            """, unsafe_allow_html=True)

# Chat input
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input("Ask AURORA anything about e-commerce...", 
                              placeholder="e.g., How do I track my order?",
                              key="user_input")

with col2:
    send_button = st.button("Send 🚀", key="send_button")

# Handle user input
if send_button and user_input.strip():
    # Add user message
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input
    })
    
    # Get bot response
    if st.session_state.chatbot:
        with st.spinner("AURORA is thinking..."):
            response_data = st.session_state.chatbot.get_response(user_input)
            
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data.get('response', 'Sorry, I could not find an answer.'),
            "source": response_data.get('source', 'unknown'),
            "confidence": response_data.get('confidence', 0.0)
        })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I'm sorry, but I'm having technical difficulties. Please try again later.",
            "source": "error"
        })
    
    # Clear input and rerun
    st.rerun()

# Footer with app info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🔒 **Secure**")
with col2:
    st.markdown("⚡ **NLTK Powered**")
with col3:
    st.markdown("🤖 **AURORA v1.0**")

# Statistics (if available)
if st.session_state.chatbot:
    stats = st.session_state.chatbot.get_conversation_stats()
    
    with st.expander("📊 Chatbot Statistics"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total FAQs", stats.get('total_faqs', 0))
        with col2:
            st.metric("Categories", stats.get('categories', 0))
        with col3:
            st.metric("OpenAI Available", "Yes" if stats.get('openai_available', False) else "No")

# Instructions
with st.expander("ℹ️ How to use AURORA"):
    st.markdown("""
    **Welcome to AURORA - Your E-Commerce AI Assistant!**
    
    🔹 **Ask Questions**: Type any question about products, shipping, returns, payments, or accounts
    
    🔹 **Use Categories**: Click category buttons in the sidebar to see common questions
    
    🔹 **Quick Questions**: Click on suggested questions to get instant answers
    
    🔹 **Examples**:
    - "How do I track my order?"
    - "What is your return policy?"
    - "How do I reset my password?"
    - "Do you ship internationally?"
    
    **AURORA uses advanced NLP to understand your questions and provide accurate answers from our comprehensive FAQ database!**
    """)