from typing import List, Dict, Any
from .embedding_service import EmbeddingService
from .vector_service import VectorService
from ..config import settings

class SearchService:
    def __init__(self):
        # These would be injected in a real application
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService(url=settings.WEAVIATE_URL, api_key=settings.WEAVIATE_API_KEY)

    async def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Performs a semantic search.
        """
        # 1. Generate embedding for the query
        query_vector = self.embedding_service.generate_embeddings([query])[0]

        # 2. Search in the vector database
        results = self.vector_service.semantic_search(query_vector, top_k)

        # 3. Format results
        formatted_results = [
            {
                "document_id": res.get("document_id"),
                "content": res.get("content"),
                "score": 1 - res.get("_additional", {}).get("distance", 1.0)
            }
            for res in results
        ]
        return formatted_results

search_service = SearchService()
