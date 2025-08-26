from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from .. import schemas, models, dependencies
from ..services.document_service import DocumentService
from ..database import get_db

router = APIRouter()

@router.post("/upload", response_model=schemas.DocumentUploadResponse, status_code=202, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.user.User = Depends(dependencies.get_current_user),
):
    """
    Upload a document for processing.
    - Detects file type (PDF, DOCX, audio).
    - Saves the file to a shared volume.
    - Creates a database record.
    - Dispatches a task to the appropriate Celery worker.
    """
    document, task_id = await DocumentService.create_upload_document(db, file, current_user.id)
    return {"document": document, "task_id": task_id}


@router.get("/{document_id}/status", response_model=schemas.DocumentRead, tags=["Documents"])
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.user.User = Depends(dependencies.get_current_user),
):
    """
    Get the processing status of a specific document.
    """
    document = await DocumentService.get_document_status(db, document_id, current_user.id)
    return document
