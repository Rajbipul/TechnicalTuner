import streamlit as st
import tempfile
import os
from backend import AutomobileRAG

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MechanicMind AI",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- VIBRANT & INTERACTIVE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #ffffff;
    }

    /* Animated Gradient Header */
    .main-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        padding: 20px 0;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Modern Chat Bubble: User */
    .user-bubble {
        background: #f0f2f6;
        color: #1f2937;
        padding: 15px 20px;
        border-radius: 25px 25px 5px 25px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }

    /* Modern Chat Bubble: Assistant */
    .assistant-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        max-width: 100%;
        float: left;
        clear: both;
        border-left: 5px solid #3b82f6;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.03);
    }

    /* Interactive Input Box */
    [data-testid="stChatInput"] {
        border: 2px solid transparent !important;
        background-image: linear-gradient(white, white), linear-gradient(to right, #3b82f6, #8b5cf6) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        border-radius: 30px !important;
    }

    /* Italic Placeholder Placeholder */
    input::placeholder {
        font-style: italic;
        background: linear-gradient(to right, #6b7280, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    input { font-style: normal !important; color: #1f2937 !important; }

    /* Custom Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
    }
    
    .stButton>button {
        border-radius: 20px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">MechanicMind AI</div>', unsafe_allow_html=True)

# --- INITIALIZATION ---
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AutomobileRAG()
    st.session_state.chat_history = []
    st.session_state.indexed_files = set()
    st.session_state.vectorstore_ready = False

# --- SIDEBAR (WORKSHOP CONSOLE) ---
with st.sidebar:
    st.markdown("### 🛠️ **Workshop Console**")
    st.write("Feed the AI with vehicle manuals.")
    
    uploaded_files = st.file_uploader(
        "Drop Service Manuals Here", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.indexed_files:
                with st.status(f"🛠️ Indexing {uploaded_file.name}...", expanded=False) as status:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        path = tmp.name
                    
                    st.session_state.rag_engine.process_document(path)
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.session_state.vectorstore_ready = True 
                    status.update(label=f"✅ {uploaded_file.name} Synced", state="complete")
                    os.remove(path)
    
    st.divider()
    if st.button("🗑️ Clear Workshop History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.indexed_files = set()
        st.session_state.vectorstore_ready = False
        st.session_state.rag_engine = AutomobileRAG()
        st.rerun()

# --- CHAT DISPLAY ---
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-card">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT AREA ---
if prompt := st.chat_input("Ask a technical question..."):
    if not st.session_state.get("vectorstore_ready", False):
        st.warning("⚠️ **Workshop Offline:** Please upload a manual in the console first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="🏎️"):
            with st.spinner("🔧 Analyzing specifications..."):
                response = st.session_state.rag_engine.get_response(prompt)
                answer = response["answer"]
                st.markdown(f'<div class="assistant-card">{answer}</div>', unsafe_allow_html=True)
                
                with st.expander("🔍 Inspection Records (Sources)"):
                    for doc in response.get("source_documents", []):
                        st.caption(f"📍 Page {doc.metadata.get('page', 0) + 1}")
                        st.info(doc.page_content[:250] + "...")
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
