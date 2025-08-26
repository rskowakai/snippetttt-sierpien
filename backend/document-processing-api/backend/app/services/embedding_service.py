from sentence_transformers import SentenceTransformer
from typing import List
from functools import lru_cache
from ..config import settings

@lru_cache(maxsize=1)
def get_embedding_model():
    """Loads and caches the sentence transformer model."""
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

class EmbeddingService:
    def __init__(self):
        self.model = get_embedding_model()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
