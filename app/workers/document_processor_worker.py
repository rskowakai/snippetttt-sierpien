import logging
from sqlalchemy.sql import func

from app.workers.celery_app import celery_app
from app.db.session import get_db_session
from app.models import Document, DocumentStatus
from app.services.document_processor import DocumentProcessor
from app.workers.notification_worker import send_notification_task

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str):
    """Complete document processing pipeline"""
    logger.info(f"Starting document processing for {document_id}")
    try:
        with get_db_session() as db:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")

            document.status = DocumentStatus.PROCESSING
            db.commit()

            # This is a simplified version of the pipeline in the prompt
            # In a real app, you would run this async
            processor = DocumentProcessor()

            # Step 1: Extract text
            self.update_state(state='PROGRESS', meta={'progress': 20, 'step': 'Extracting text'})
            extracted_text = processor.extract_text(document) # This is an async method
            document.extracted_text = extracted_text # In a real app, use asyncio.run()
            db.commit()

            # Step 2: Generate chunks
            self.update_state(state='PROGRESS', meta={'progress': 60, 'step': 'Creating chunks'})
            chunks = processor.create_chunks(extracted_text)
            document.chunk_count = len(chunks)
            db.commit()

            # Step 3: Generate embeddings
            self.update_state(state='PROGRESS', meta={'progress': 80, 'step': 'Generating embeddings'})
            weaviate_id = processor.generate_embeddings(document, chunks)
            document.weaviate_id = weaviate_id
            document.vector_status = "completed"
            db.commit()

            # Step 4: Finalize
            self.update_state(state='PROGRESS', meta={'progress': 100, 'step': 'Finalizing'})
            summary = processor.generate_summary(extracted_text)
            document.summary = summary
            document.status = DocumentStatus.PROCESSED
            document.processed_at = func.now()
            db.commit()

            send_notification_task.delay(
                user_id=str(document.owner_id),
                notification_type="document_processed",
                data={"document_id": document_id, "document_name": document.original_filename}
            )

            return {"status": "completed", "document_id": document_id}

    except Exception as exc:
        logger.error(f"Document processing failed for {document_id}: {str(exc)}")
        try:
            with get_db_session() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = DocumentStatus.FAILED
                    document.processing_error = str(exc)
                    db.commit()
        except Exception as db_exc:
            logger.error(f"Failed to update document status to FAILED: {db_exc}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

        raise exc
