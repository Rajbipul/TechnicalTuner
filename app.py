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

# --- REFINED INTERFACE STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #ffffff;
    }

    /* 1. Header with Vibrant Gradient */
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
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. Chat Visibility (Black Text) */
    .user-bubble, .assistant-card, .stMarkdown p {
        color: #000000 !important;
    }

    /* 3. WORKSHOP CONSOLE: Grey Sidebar & Black Text Fix */
    [data-testid="stSidebar"] {
        background-color: #f2f2f2 !important; 
        border-right: 1px solid #d1d1d1;
    }
    
    /* Ensure MB, Filenames, and labels in sidebar are BLACK */
    [data-testid="stSidebar"] *, 
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }

    /* 4. RESET BUTTON: Hover scale animation, color stays black */
    div.stButton > button {
        background-color: #333333 !important;
        color: white !important;
        border-radius: 25px !important;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border: none !important;
    }
    div.stButton > button:hover {
        transform: scale(1.1) !important; /* Becomes larger */
        background-color: #333333 !important; /* Color does not change */
        color: white !important;
    }

    /* 5. CHAT INPUT: White text while writing */
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    
    [data-testid="stChatInput"] {
        border-radius: 35px !important;
        border: 2px solid transparent !important;
        background-image: linear-gradient(#1a1a1a, #1a1a1a), 
                          linear-gradient(to right, #00c6ff, #bc4e9c) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
    }

    input::placeholder {
        font-style: italic;
        color: #aaaaaa !important;
    }
    
    /* Chat bubbles for better aesthetics */
    .user-bubble {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        padding: 14px 22px;
        border-radius: 22px 22px 4px 22px;
        margin: 12px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .assistant-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 18px;
        margin: 18px 0;
        max-width: 100%;
        float: left;
        clear: both;
        border-left: 6px solid;
        border-image: linear-gradient(to bottom, #00c6ff, #f80759) 1;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
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

# --- SIDEBAR (GREY WORKSHOP CONSOLE) ---
with st.sidebar:
    st.markdown("### 🛠️ Workshop Console")
    st.write("Manage your vehicle manuals and system state.")
    
    uploaded_files = st.file_uploader(
        "Upload Technical Manuals", 
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
                    status.update(label=f"✅ {uploaded_file.name} Loaded", state="complete")
                    os.remove(path)
    
    st.divider()
    if st.button("🗑️ Reset All Data", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.indexed_files = set()
        st.session_state.vectorstore_ready = False
        st.session_state.rag_engine = AutomobileRAG()
        st.rerun()

# --- CHAT DISPLAY ---
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-card">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT AREA ---
if prompt := st.chat_input("Ask a technical question..."):
    if not st.session_state.get("vectorstore_ready", False):
        st.warning("⚠️ Workshop Offline: Please upload a manual to begin.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="🏎️"):
            with st.spinner("⚡ Scanning database..."):
                response = st.session_state.rag_engine.get_response(prompt)
                answer = response["answer"]
                st.markdown(f'<div class="assistant-card">{answer}</div>', unsafe_allow_html=True)
                
                with st.expander("📖 View Verified Sources"):
                    for doc in response.get("source_documents", []):
                        st.caption(f"📍 Manual Extract | Page {doc.metadata.get('page', 0) + 1}")
                        st.info(doc.page_content[:250] + "...")
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
