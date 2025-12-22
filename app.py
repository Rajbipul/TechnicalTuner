import streamlit as st
import tempfile
import os
from backend import AutomobileRAG

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AutoSpec Pro | AI Workshop Assistant",
    layout="wide"
)

# --- IMPROVED CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    
    .title-text {
        text-align: center;
        color: #1E1E1E;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    /* SIDEBAR FIX: High Contrast Dark Mode */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        color: #ffffff !important;
    }

    /* Force Sidebar labels and text to be white */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stHeader {
        color: #ffffff !important;
    }

    /* Fix File Uploader visibility in dark sidebar */
    [data-testid="stSidebar"] .stFileUploader section {
        background-color: #1f2937 !important;
        color: white !important;
        border: 1px dashed #4b5563;
    }

    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #e74c3c;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #1a1a1a;
    }
    
    .stButton>button {
        background-color: #e74c3c !important;
        color: white !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="title-text">🏎️ AutoSpec Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666;">Automobile Knowledge Engine & Diagnostic Assistant</p>', unsafe_allow_html=True)
st.divider()

# --- INITIALIZATION ---
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AutomobileRAG()
    st.session_state.chat_history = []
    st.session_state.processed_file = None

# --- SIDEBAR: MULTI-FILE UPLOAD ---
with st.sidebar:
    st.header(" Workshop Console")
    # Change to accept_multiple_files=True
    uploaded_files = st.file_uploader(
        "Upload Manuals (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Initialize tracking set if it doesn't exist
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        for uploaded_file in uploaded_files:
            # Index each file ONLY if it hasn't been processed yet
            if uploaded_file.name not in st.session_state.indexed_files:
                with st.status(f" Indexing {uploaded_file.name}...", expanded=False) as status:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        path = tmp.name
                    
                    # Backend appends to FAISS instead of overwriting
                    num_chunks = st.session_state.rag_engine.process_document(path)
                    
                    # Track this file and enable the chat
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.session_state.vectorstore_ready = True 
                    
                    status.update(label=f" {uploaded_file.name} added!", state="complete")
                    os.remove(path)
            else:
                st.write(f" {uploaded_file.name} already in memory.")

    st.divider()
    if st.button(" Reset Workshop Memory"):
        st.session_state.chat_history = []
        st.session_state.indexed_files = set()
        st.session_state.vectorstore_ready = False
        st.session_state.rag_engine = AutomobileRAG() # Re-init backend
        st.rerun()

# --- CHAT DISPLAY ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f'<div class="result-card">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask a technical question..."):
    # Fix: Check the boolean flag instead of a filename string
    if not st.session_state.get("vectorstore_ready", False):
        st.error("Please upload a service manual in the sidebar first!")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(" Analyzing vehicle data..."):
                response = st.session_state.rag_engine.get_response(prompt)
                answer = response["answer"]
                
                st.markdown(f'<div class="result-card">{answer}</div>', unsafe_allow_html=True)
                
                with st.expander(" View Technical Sources"):
                    for doc in response.get("source_documents", []):
                        st.caption(f"**Page {doc.metadata.get('page', 0) + 1}:**")
                        st.info(doc.page_content[:300] + "...")
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
