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

# --- VIBRANT GRADIENT UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #ffffff;
    }

    /* 1. Gradient Animated Header */
    .main-header {
        background: linear-gradient(-45deg, #00c6ff, #0072ff, #bc4e9c, #f80759);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        padding: 25px 0;
        letter-spacing: -1px;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. User Message: Blue-Purple Gradient Bubble */
    .user-bubble {
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        padding: 14px 22px;
        border-radius: 22px 22px 4px 22px;
        margin: 12px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(37, 117, 252, 0.2);
    }

    /* 3. Assistant Card: Subtle Multi-color Left Border */
    .assistant-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 18px;
        margin: 18px 0;
        max-width: 100%;
        float: left;
        clear: both;
        border-image: linear-gradient(to bottom, #00c6ff, #0072ff) 1;
        border-left: 6px solid;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        line-height: 1.6;
        color: #2d3436;
    }

    /* 4. Interactive Gradient Input Bar */
    [data-testid="stChatInput"] {
        border-radius: 35px !important;
        border: 2px solid transparent !important;
        background-image: linear-gradient(white, white), 
                          linear-gradient(to right, #00c6ff, #0072ff, #bc4e9c) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        padding: 8px !important;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stChatInput"]:focus-within {
        transform: scale(1.01);
    }

    /* Italic Gradient Placeholder */
    input::placeholder {
        font-style: italic;
        background: linear-gradient(to right, #00b4db, #0083b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 5. Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
    }

    .stButton>button {
        background: linear-gradient(to right, #141e30, #243b55) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
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
    st.write("Upload service manuals to index documentation.")
    
    uploaded_files = st.file_uploader(
        "Drop Service Manuals Here", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.indexed_files:
                with st.status(f"⚙️ Syncing {uploaded_file.name}...", expanded=False) as status:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        path = tmp.name
                    
                    st.session_state.rag_engine.process_document(path)
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.session_state.vectorstore_ready = True 
                    status.update(label=f"✅ {uploaded_file.name} Loaded", state="complete")
                    os.remove(path)
    
    st.divider()
    if st.button("🗑️ Clear All Sessions", use_container_width=True):
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
        st.warning("⚠️ **System Offline:** Please upload a manual in the console to begin.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="🏎️"):
            with st.spinner("⚡ Retrieving Specifications..."):
                response = st.session_state.rag_engine.get_response(prompt)
                answer = response["answer"]
                st.markdown(f'<div class="assistant-card">{answer}</div>', unsafe_allow_html=True)
                
                with st.expander("📖 View Verified Data Sources"):
                    for doc in response.get("source_documents", []):
                        st.caption(f"📍 Manual Extract | Page {doc.metadata.get('page', 0) + 1}")
                        st.info(doc.page_content[:250] + "...")
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
