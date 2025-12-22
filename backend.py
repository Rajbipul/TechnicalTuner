import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.prompts import PromptTemplate

load_dotenv()

class AutomobileRAG:
    def __init__(self):
        # 1. Initialize Embeddings (Hugging Face)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        # 2. Setup Memory for Chat History
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True, 
            output_key='answer'
        )

    def process_document(self, pdf_path):
        """Clean, Split, and Append the PDF to the Vector Store"""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(documents)
        
        # --- IMPROVED MULTI-PDF LOGIC ---
        if self.vectorstore is None:
            # Create the initial vector store
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            # Add new chunks to the existing vector store
            self.vectorstore.add_documents(chunks)
            
        return len(chunks)

    def get_response(self, question):
        """Query the LLM with Context and a Detailed Prompt"""
        if not self.vectorstore:
            return "Please upload a document first."

        # Define a detailed custom prompt for the LLM
        custom_template = """
        You are an expert automobile technician and technical advisor.
        Use the following pieces of retrieved context to answer the user's question in a detailed, comprehensive, and step-by-step format.
        
        Instructions:
        1. Provide technical specifications, torque values, or fluid types exactly as found in the text.
        2. If describing a procedure, use a numbered list for clarity.
        3. Include warnings or 'Notes' if they are mentioned in the context.
        4. If the answer is not in the context, say you don't know; do not make up information.
        5. Structure the response with clear headings if multiple parts are discussed.

        Context:
        {context}

        Question: 
        {question}

        Detailed Technical Answer:
        """
        
        QA_PROMPT = PromptTemplate(
            template=custom_template, input_variables=["context", "question"]
        )

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        # Build the RAG Chain with the custom prompt
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}), # Increased 'k' for more context
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT}
        )
        
        return chain.invoke({"question": question})