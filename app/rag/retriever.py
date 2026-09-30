from app.rag.chunker import load_and_chunk_documents
from app.rag.vectorstore import FitnessVectorStore
import os

class FitnessRetriever:
    def __init__(self, config):
        self.config = config
        os.makedirs(self.config.CHROMA_PERSIST_DIR, exist_ok=True)
        self.vectorstore = FitnessVectorStore(
            persist_dir=self.config.CHROMA_PERSIST_DIR,
            embedding_model=self.config.EMBEDDING_MODEL
        )
        
    def ingest_knowledge_base(self):
        chunks = load_and_chunk_documents(
            self.config.KNOWLEDGE_BASE_DIR,
            self.config.CHUNK_SIZE,
            self.config.CHUNK_OVERLAP
        )
        self.vectorstore.ingest(chunks)
        return len(chunks)
        
    def retrieve(self, query: str, top_k: int = 5) -> dict:
        results = self.vectorstore.query(query, top_k)
        if not results:
            return {"context": "", "sources": []}
            
        context_parts = []
        sources = set()
        
        for res in results:
            source = res['metadata'].get('source', 'Unknown')
            section = res['metadata'].get('section', '')
            sources.add(source)
            
            header = f"Source: {source}"
            if section:
                header += f" (Section: {section})"
                
            context_parts.append(f"{header}\n{res['text']}")
            
        return {
            "context": "\n\n---\n\n".join(context_parts),
            "sources": list(sources)
        }
        
    def get_status(self) -> dict:
        return {
            "document_count": self.vectorstore.get_collection_count(),
            "status": "ready"
        }
