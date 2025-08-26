from ..celery_app import celery_app
from ..database import AsyncSessionLocal
from ..models.document import Document, DocumentStatus
from ..services.embedding_service import EmbeddingService
from ..services.vector_service import VectorService
from ..services.gemini_service import gemini_service # Import singleton instance
from ..utils.text_processor import extract_text_from_pdf, extract_text_from_docx, chunk_text
from ..config import settings
from sqlalchemy.future import select
import logging
import asyncio

logger = logging.getLogger(__name__)

async def get_document_and_update_status(document_id: int, status: DocumentStatus, metadata_update: dict = None, error_message: str = None):
    """Helper to fetch a document and update its status/metadata in the DB."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(Document).where(Document.id == document_id)
            result = await session.execute(query)
            document = result.scalar_one_or_none()
            if document:
                document.status = status
                current_meta = document.metadata or {}
                if metadata_update:
                    current_meta.update(metadata_update)
                if error_message:
                    current_meta["error"] = error_message
                document.metadata = current_meta
                await session.commit()
                await session.refresh(document)
            return document

@celery_app.task(name="process_document", bind=True)
def process_document_task(self, document_id: int, file_path: str, mime_type: str):
    """
    Celery task to process a text-based document:
    1. Extract text.
    2. Generate a summary with Gemini.
    3. Chunk text.
    4. Generate embeddings.
    5. Save to vector DB.
    """
    logger.info(f"Starting processing for document_id: {document_id}")

    try:
        document = asyncio.run(get_document_and_update_status(document_id, DocumentStatus.PROCESSING))
        if not document:
            raise ValueError("Document not found in database.")

        # 1. Extract text
        logger.info(f"Extracting text from {file_path}...")
        text_content = ""
        if mime_type == "application/pdf":
            text_content = extract_text_from_pdf(file_path)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text_content = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported mime type: {mime_type}")

        if not text_content.strip():
            logger.warning(f"No text could be extracted from document {document_id}.")
            asyncio.run(get_document_and_update_status(document_id, DocumentStatus.COMPLETED, metadata_update={"summary": "No text content found."}))
            return {"document_id": document_id, "status": "completed_no_text"}

        # 2. Generate summary with Gemini
        logger.info(f"Generating summary for document {document_id} with Gemini...")
        summary = gemini_service.generate_summary(text_content)
        asyncio.run(get_document_and_update_status(document_id, DocumentStatus.PROCESSING, metadata_update={"summary": summary}))
        logger.info(f"Summary generated for document {document_id}.")

        # 3. Chunk text
        logger.info("Chunking text...")
        chunks = chunk_text(text_content)

        # 4. Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embedding_service = EmbeddingService()
        vectors = embedding_service.generate_embeddings(chunks)

        # 5. Save to Weaviate
        logger.info("Saving chunks and vectors to Weaviate...")
        vector_service = VectorService(url=settings.WEAVIATE_URL, api_key=settings.WEAVIATE_API_KEY)
        vector_service.add_document_chunks(
            document_id=document_id,
            filename=document.filename,
            chunks=chunks,
            vectors=vectors
        )

        # 6. Update status to COMPLETED
        asyncio.run(get_document_and_update_status(document_id, DocumentStatus.COMPLETED))
        logger.info(f"Successfully processed document_id: {document_id}")

    except Exception as e:
        logger.error(f"Failed to process document_id: {document_id}. Error: {e}", exc_info=True)
        asyncio.run(get_document_and_update_status(document_id, DocumentStatus.FAILED, error_message=str(e)))
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})

    return {"document_id": document_id, "status": "processing_finished"}
