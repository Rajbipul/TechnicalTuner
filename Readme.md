# 🛠️ MechanicMind AI: Intelligent Automotive Documentation Assistant

**MechanicMind AI** is an advanced Retrieval-Augmented Generation (RAG) platform tailored for the automotive industry. It enables users to process vehicle owner manuals and Diagnostic Trouble Code (DTC) databases to extract precise technical data and repair guidance using artificial intelligence.

### 🚀 Application Access

**[Launch the Interactive App](https://rag-powered-assistant.streamlit.app/)** *(Note: Valid API credentials may be required for full functionality)*.

---

## ✨ Core Capabilities

* **Bulk Document Indexing:** Seamlessly upload and organize multiple service manuals at the same time.
* **Precision Engineering Insights:** Delivers specific torque values, fluid capacities, and detailed repair walkthroughs.
* **Contextual Dialogue:** Utilizes conversational memory to ensure troubleshooting sessions feel natural and continuous.
* **Verified Sourcing:** Every response is backed by citations, identifying the exact page and manual used for the information.
* **Industrial-Grade UI:** Features a high-contrast interface designed specifically for high-visibility use in workshop environments.

---

## 💻 Technology Framework

* **Frontend Interface:** [Streamlit](https://streamlit.io/)
* **Inference Engine:** [Google Gemini 2.5 Flash](https://aistudio.google.com/)
* **Vector Embeddings:** [Hugging Face Sentence Transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
* **Similarity Search:** [FAISS (Facebook AI Similarity Search)](https://github.com/facebookresearch/faiss)
* **LLM Orchestration:** [LangChain](https://www.langchain.com/)

---

## 🔧 Installation & Deployment

### 1. Streamlit Community Cloud
To host this on Streamlit Cloud, ensure your repository structure includes `app.py`, `backend.py`, and `requirements.txt`. 

**Important:** Do not upload sensitive keys to GitHub. Instead, configure your **Secrets** in the Streamlit Dashboard as follows:
```toml
GOOGLE_API_KEY = "your_gemini_api_key"
HUGGINGFACEHUB_API_TOKEN = "your_huggingface_token"

# Download the source code
git clone [https://github.com/yourusername/mechanicmind-ai.git](https://github.com/yourusername/mechanicmind-ai.git)
cd mechanicmind-ai

# Initialize a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows users: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Launch the local server
streamlit run app.py
