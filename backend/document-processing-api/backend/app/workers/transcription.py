from ..celery_app import celery_app
from ..database import AsyncSessionLocal
from ..models.document import Document, DocumentStatus
from sqlalchemy.future import select
import logging
import whisper
import asyncio

logger = logging.getLogger(__name__)

# Load model once when the worker starts
model = whisper.load_model("base")

async def update_transcription_status(document_id: int, status: DocumentStatus, transcript: str = None, error_message: str = None):
    """Helper to update document status and transcription in DB."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(Document).where(Document.id == document_id)
            result = await session.execute(query)
            document = result.scalar_one_or_none()
            if document:
                document.status = status
                if transcript:
                    document.transcription = transcript
                if error_message:
                    document.metadata = {**document.metadata, "error": error_message}
                await session.commit()

@celery_app.task(name="transcribe_audio", bind=True)
def transcribe_audio_task(self, document_id: int, file_path: str):
    """
    Celery task to transcribe an audio file using OpenAI Whisper.
    """
    logger.info(f"Starting transcription for document_id: {document_id}")

    try:
        asyncio.run(update_transcription_status(document_id, DocumentStatus.PROCESSING))

        # Perform transcription
        result = model.transcribe(file_path, fp16=False)
        transcript = result["text"]

        # Update DB with the transcript and set status to COMPLETED
        asyncio.run(update_transcription_status(document_id, DocumentStatus.COMPLETED, transcript=transcript))
        logger.info(f"Transcription complete for document_id: {document_id}")

        # Optional: Here you could dispatch another task to embed the transcript
        # process_document_task.delay(...)

    except Exception as e:
        logger.error(f"Transcription failed for document_id: {document_id}. Error: {e}", exc_info=True)
        asyncio.run(update_transcription_status(document_id, DocumentStatus.FAILED, error_message=str(e)))
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})

    return {"document_id": document_id, "status": "transcription_finished"}
