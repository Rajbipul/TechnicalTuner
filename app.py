import streamlit as st
import tempfile
import os
from backend import AutomobileRAG

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MechanicMind AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GEMINI-INSPIRED CSS ---
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }

    /* Minimalist Header */
    .gemini-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        padding: 15px 30px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        z-index: 99;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Floating Bubble / Toggle Button */
    .bubble-btn {
        background: #f0f4f9;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.3s;
    }
    .bubble-btn:hover { background: #e2e7ef; }

    /* Chat Area Centering */
    .main-chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 80px;
        padding-bottom: 150px;
    }

    /* Italic Placeholder Logic */
    input::placeholder {
        font-style: italic;
        color: #757575 !important;
    }
    input { font-style: normal !important; }

    /* User Message Bubble */
    .user-msg {
        background-color: #f0f4f9;
        padding: 12px 20px;
        border-radius: 20px;
        display: inline-block;
        margin: 10px 0;
        max-width: 85%;
        float: right;
        clear: both;
    }

    /* Assistant Message (No Bubble, just text) */
    .assistant-msg {
        padding: 20px 0;
        margin: 10px 0;
        max-width: 100%;
        float: left;
        clear: both;
    }

    /* Fixed Bottom Input */
    [data-testid="stChatInput"] {
        max-width: 800px !important;
        margin: 0 auto !important;
        bottom: 30px !important;
        background-color: #f0f4f9 !important;
        border-radius: 28px !important;
        border: none !important;
        padding: 5px !important;
    }

    /* Hide default streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AutomobileRAG()
    st.session_state.chat_history = []
    st.session_state.indexed_files = set()
    st.session_state.vectorstore_ready = False

# --- CUSTOM HEADER ---
st.markdown("""
    <div class="gemini-header">
        <div style="font-weight: 600; font-size: 20px; color: #444746;">MechanicMind AI</div>
        <div style="color: #444746; font-size: 14px;">Workshop Assistant</div>
    </div>
""", unsafe_allow_html=True)

# --- WORKSHOP CONSOLE (Sidebar) ---
with st.sidebar:
    st.title("🛠️ Workshop Console")
    st.caption("Upload manuals to provide context for the AI.")
    
    uploaded_files = st.file_uploader(
        "Upload Manuals (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.indexed_files:
                with st.status(f"Indexing {uploaded_file.name}...", expanded=False) as status:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        path = tmp.name
                    
                    st.session_state.rag_engine.process_document(path)
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.session_state.vectorstore_ready = True 
                    status.update(label=f"{uploaded_file.name} Added", state="complete")
                    os.remove(path)
    
    if st.button("Reset Memory", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.indexed_files = set()
        st.session_state.vectorstore_ready = False
        st.session_state.rag_engine = AutomobileRAG()
        st.rerun()

# --- MAIN CHAT LAYOUT ---
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'<div class="user-msg">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-msg">{message["content"]}</div>', unsafe_allow_html=True)

# Handle New Input
if prompt := st.chat_input("Ask a technical question..."):
    if not st.session_state.get("vectorstore_ready", False):
        st.warning("Please open the sidebar (top left arrow) and upload a manual first.")
    else:
        # Add User Message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

        # Assistant Response
        with st.chat_message("assistant", avatar=None): # Hidden avatar for Gemini look
            with st.spinner("Thinking..."):
                response = st.session_state.rag_engine.get_response(prompt)
                answer = response["answer"]
                st.markdown(f'<div class="assistant-msg">{answer}</div>', unsafe_allow_html=True)
                
                with st.expander("Sources"):
                    for doc in response.get("source_documents", []):
                        st.caption(f"Page {doc.metadata.get('page', 0) + 1}")
                        st.info(doc.page_content[:200] + "...")
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun() # Refresh to keep layout clean

st.markdown('</div>', unsafe_allow_html=True)
