import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend import config

def ingest_documents():
    """
    Reads documents from knowledge_base directory, splits them into chunks,
    generates OpenAI embeddings, and saves the index to a local FAISS database.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in config or environment.")

    # 1. Gather all txt files from the knowledge base directory
    kb_path = Path(config.KNOWLEDGE_BASE_DIR)
    txt_files = list(kb_path.glob("*.txt"))
    
    if not txt_files:
        print(f"No text files found in {config.KNOWLEDGE_BASE_DIR}")
        return False
    
    documents = []
    for file_path in txt_files:
        try:
            print(f"Loading document: {file_path.name}")
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents.extend(loader.load())
        except Exception as e:
            print(f"Failed to load {file_path.name}: {e}")

    if not documents:
        print("No documents loaded successfully.")
        return False

    # 2. Split documents into overlapping chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # 3. Create Google Generative AI Embeddings and FAISS Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=config.GEMINI_API_KEY,
        model=config.EMBEDDING_MODEL
    )
    
    print("Generating embeddings and building FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # 4. Save to disk
    vector_store.save_local(str(config.VECTOR_STORE_DIR))
    print(f"FAISS index successfully saved to {config.VECTOR_STORE_DIR}")
    return True

if __name__ == "__main__":
    # Allow running this module directly to trigger ingestion
    import sys
    # Add parent directory to sys.path to allow absolute imports
    sys.path.append(str(config.BASE_DIR))
    
    success = ingest_documents()
    if success:
        print("Ingestion completed successfully.")
    else:
        print("Ingestion failed.")
        sys.exit(1)
