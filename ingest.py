import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.config import config
from app.rag.retriever import FitnessRetriever

def main():
    load_dotenv()
    print(f"Loading configuration...")
    print(f"Knowledge base directory: {config.KNOWLEDGE_BASE_DIR}")
    print(f"Chroma DB directory: {config.CHROMA_PERSIST_DIR}")
    
    retriever = FitnessRetriever(config)
    
    print("Clearing existing vector store...")
    retriever.vectorstore.clear()
    
    print("Ingesting knowledge base...")
    count = retriever.ingest_knowledge_base()
    
    print(f"Success! Ingested {count} chunks into the vector store.")
    print(f"Final document count: {retriever.get_status()['document_count']}")

if __name__ == "__main__":
    main()
