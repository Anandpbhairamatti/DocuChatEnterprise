from abc import ABC, abstractmethod
from typing import List, Dict, Any

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

class VectorDBProvider(ABC):
    @abstractmethod
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        pass

    @abstractmethod
    def search(self, collection_name: str, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        pass

class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        pass

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Should return a dict containing:
        - content: str
        - prompt_tokens: int
        - completion_tokens: int
        - response_time_ms: float
        """
        pass
