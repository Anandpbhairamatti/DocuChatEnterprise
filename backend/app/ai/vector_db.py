import os
import chromadb
from typing import List, Dict, Any
from app.ai.interfaces import VectorDBProvider
from app.core.config import settings

class ChromaDBProvider(VectorDBProvider):
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            os.makedirs(settings.CHROMA_DIR, exist_ok=True)
            self._client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        return self._client

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        collection = self.client.get_or_create_collection(name=collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, collection_name: str, query_text: str, n_results: int = 5, where: dict = None) -> Dict[str, Any]:
        collection = self.client.get_or_create_collection(name=collection_name)
        
        if collection.count() == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
            
        kwargs = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        if where:
            kwargs["where"] = where
            
        results = collection.query(**kwargs)
        return results

# Dependency injection instance
vector_db_provider = ChromaDBProvider()
