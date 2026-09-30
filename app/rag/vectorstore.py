import chromadb
from chromadb.utils import embedding_functions

class FitnessVectorStore:
    def __init__(self, persist_dir: str, embedding_model: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self.collection = self.client.get_or_create_collection(
            name="fitness_kb",
            embedding_function=self.embedding_fn
        )

    def ingest(self, documents: list[dict]):
        if not documents:
            return
            
        ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_index']}" for doc in documents]
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        self.collection.upsert(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return formatted_results

    def get_collection_count(self) -> int:
        return self.collection.count()

    def clear(self):
        try:
            self.client.delete_collection("fitness_kb")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name="fitness_kb",
            embedding_function=self.embedding_fn
        )
