import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# A stub for the SearchResult dataclass used in RAG service
class SearchResult:
    def __init__(self, content: str, score: float, chunk_index: int, metadata: Dict[str, Any]):
        self.content = content
        self.score = score
        self.chunk_index = chunk_index
        self.metadata = metadata

class VectorService:
    def __init__(self, settings=None):
        logger.info("Initializing VectorService stub")

    async def search_similar(
        self,
        query_text: str,
        document_id: str,
        limit: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        logger.info(
            f"Searching for '{query_text[:50]}...' in doc {document_id} "
            f"with limit {limit} and threshold {similarity_threshold}"
        )
        # Return dummy data
        return [
            SearchResult(
                content=f"This is a dummy search result for '{query_text[:20]}'.",
                score=0.9,
                chunk_index=i,
                metadata={"source": "dummy_source"}
            ) for i in range(limit)
        ]

    async def generate_embeddings(self, document, chunks: List[str]) -> str:
        weaviate_id = f"weaviate-id-{document.id}"
        logger.info(f"Generating embeddings for document {document.id} and storing with id {weaviate_id}")
        return weaviate_id

    async def delete_document(self, weaviate_id: str):
        logger.info(f"Deleting document {weaviate_id} from vector store.")
        return True
