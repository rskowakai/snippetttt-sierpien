import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import magic

from ..models.document import Document, DocumentStatus
from ..workers.document_processor import process_document_task
from ..workers.transcription import transcribe_audio_task

UPLOAD_DIR = "/app/shared_uploads" # Shared volume for app and workers
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentService:
    @staticmethod
    async def create_upload_document(
        db: AsyncSession,
        file: UploadFile,
        user_id: uuid.UUID
    ) -> (Document, str):
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()

        # Detect file type to route to the correct worker
        mime_type = magic.from_file(file_path, mime=True)

        db_document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            status=DocumentStatus.PENDING,
            metadata={"mime_type": mime_type}
        )
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)

        # Dispatch the correct Celery task based on mime type
        task = None
        if mime_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            task = process_document_task.delay(document_id=db_document.id, file_path=file_path, mime_type=mime_type)
        elif mime_type in ["audio/mpeg", "audio/wav", "audio/x-wav"]:
            task = transcribe_audio_task.delay(document_id=db_document.id, file_path=file_path)
        else:
            # Clean up file and fail the process
            os.remove(file_path)
            db_document.status = DocumentStatus.FAILED
            db_document.metadata["error"] = f"Unsupported file type: {mime_type}"
            await db.commit()
            raise HTTPException(status_code=400, detail=f"File type {mime_type} not supported.")

        db_document.task_id = task.id
        await db.commit()
        await db.refresh(db_document)

        return db_document, task.id

    @staticmethod
    async def get_document_status(db: AsyncSession, document_id: int, user_id: uuid.UUID) -> Document:
        query = select(Document).where(Document.id == document_id, Document.user_id == user_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
