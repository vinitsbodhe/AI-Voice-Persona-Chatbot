import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend import config

class PersonaRetriever:
    def __init__(self):
        """
        Initializes the retriever by loading the FAISS database from disk.
        """
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in config or environment.")
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=config.GEMINI_API_KEY,
            model=config.EMBEDDING_MODEL
        )
        self.vector_store = None
        self.load_index()

    def load_index(self):
        """
        Loads the FAISS index from the local directory if it exists.
        """
        index_path = Path(config.VECTOR_STORE_DIR)
        # FAISS index files have extensions .faiss and .pkl
        if (index_path / "index.faiss").exists() and (index_path / "index.pkl").exists():
            print("Loading local FAISS index...")
            # allow_dangerous_deserialization is required for FAISS local loading in modern langchain
            self.vector_store = FAISS.load_local(
                str(config.VECTOR_STORE_DIR),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("FAISS index files not found. Ingestion is required first.")
            self.vector_store = None

    def retrieve(self, query: str, k: int = 3) -> list:
        """
        Performs vector search and retrieves top k relevant document chunks.
        """
        if self.vector_store is None:
            # Try reloading in case it was created after initialization
            self.load_index()
            
        if self.vector_store is None:
            print("Retriever warning: FAISS vector store is not initialized. Returning empty context.")
            return []

        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

# Test execution helper
if __name__ == "__main__":
    import sys
    sys.path.append(str(config.BASE_DIR))
    
    retriever = PersonaRetriever()
    test_query = "What projects have you worked on?"
    results = retriever.retrieve(test_query, k=2)
    print(f"\nQuery: {test_query}\n")
    for idx, doc in enumerate(results):
        print(f"Result {idx+1}:")
        print(doc.page_content)
        print(doc.metadata)
        print("-" * 40)
