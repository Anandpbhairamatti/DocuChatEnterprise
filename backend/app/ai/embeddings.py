from sentence_transformers import SentenceTransformer
from typing import List
from app.ai.interfaces import EmbeddingProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

# Dependency injection instance
embedding_provider = SentenceTransformerProvider()
