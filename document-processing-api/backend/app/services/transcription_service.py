import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    @staticmethod
    def start_transcription(document_id: int, file_path: str) -> str:
        """
        Dispatches a transcription task to the Celery worker.
        """
        from ..workers.transcription import transcribe_audio_task

        logger.info(f"Dispatching transcription task for document {document_id}")
        task = transcribe_audio_task.delay(document_id=document_id, file_path=file_path)
        return task.id

transcription_service = TranscriptionService()
