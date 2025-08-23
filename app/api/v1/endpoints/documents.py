import logging
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import User, Query
from app.db.session import get_db
from app.api.dependencies import (
    get_current_active_user, check_rate_limit,
    check_usage_limits, log_query_metrics
)
from app.services.rag_service import EnhancedRAGService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    id: str
    question: str
    answer: str
    confidence_score: float
    processing_time: float
    query_type: str
    citations: List[Dict[str, Any]]
    suggestions: List[str]

# A stub for the RAG service dependency
def get_rag_service():
    return EnhancedRAGService(settings)

@router.post("/{document_id}/query", response_model=QueryResponse)
async def query_document(
    document_id: str,
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    rag_service: EnhancedRAGService = Depends(get_rag_service)
):
    """Process a query against a specific document"""

    await check_rate_limit(str(current_user.id), "query")

    if not await check_usage_limits(current_user, "query", db):
        raise HTTPException(
            status_code=429,
            detail="Monthly query limit exceeded"
        )

    try:
        query_result = await rag_service.process_query(
            question=request.question,
            document_id=document_id,
            user=current_user,
            db=db,
            context=request.context
        )

        background_tasks.add_task(
            log_query_metrics,
            query_result.id,
            current_user.id,
            query_result.processing_time
        )

        suggestions = await rag_service.generate_follow_up_questions(
            query_result.question, query_result.answer, document_id
        )

        return QueryResponse(
            id=str(query_result.id),
            question=query_result.question,
            answer=query_result.answer,
            confidence_score=query_result.confidence_score,
            processing_time=query_result.processing_time,
            query_type=query_result.query_type.value,
            citations=await rag_service.extract_citations(query_result),
            suggestions=suggestions
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) # 404 for not found
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Placeholder for document upload, needed for tests
@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "original_filename": file.filename,
        "status": "uploaded"
    }

# Placeholder for getting documents, needed for tests
@router.get("")
async def get_documents(current_user: User = Depends(get_current_active_user)):
    return []
