from fastapi import APIRouter, Depends
from typing import List

from .. import schemas, models, dependencies
from ..services.vector_service import VectorService
from ..services.embedding_service import EmbeddingService
from ..config import settings

router = APIRouter()

@router.post("/", response_model=List[schemas.SearchResult], tags=["Search"])
async def search_documents(
    query: schemas.SearchQuery,
    current_user: models.user.User = Depends(dependencies.get_current_user),
):
    """
    Perform a semantic search across all processed documents.
    Generates an embedding for the query and searches in Weaviate.
    """
    # In a real app, you'd inject these services properly using Depends
    embedding_service = EmbeddingService()
    vector_service = VectorService(url=settings.WEAVIATE_URL, api_key=settings.WEAVIATE_API_KEY)

    # 1. Generate embedding for the user's query
    query_vector = embedding_service.generate_embeddings([query.query])[0]

    # 2. Perform search in Weaviate
    search_results = vector_service.semantic_search(query_vector, query.top_k)

    # 3. Format the response
    formatted_results = []
    for res in search_results:
        formatted_results.append(
            schemas.SearchResult(
                document_id=res["document_id"],
                content=res["content"],
                score=1 - res["_additional"]["distance"], # Convert distance to similarity score
            )
        )

    return formatted_results
