import weaviate
from weaviate.auth import AuthApiKey
import uuid
from typing import List, Dict, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)

WEAVIATE_CLASS_NAME = "DocumentChunk"

class VectorService:
    def __init__(self, url: str, api_key: str | None = None):
        auth_config = AuthApiKey(api_key=api_key) if api_key else None
        self.client = weaviate.Client(url=url, auth_client_secret=auth_config)

    def initialize_schema(self):
        """Creates the DocumentChunk schema in Weaviate if it doesn't exist."""
        if self.client.schema.exists(WEAVIATE_CLASS_NAME):
            logger.info(f"Schema '{WEAVIATE_CLASS_NAME}' already exists.")
            return

        schema = {
            "class": WEAVIATE_CLASS_NAME,
            "description": "A chunk of text from a document",
            "vectorizer": "none", # We will provide our own vectors
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "document_id", "dataType": ["int"]},
                {"name": "filename", "dataType": ["text"]},
            ],
        }
        self.client.schema.create_class(schema)
        logger.info(f"Schema '{WEAVIATE_CLASS_NAME}' created successfully.")

    def add_document_chunks(self, document_id: int, filename: str, chunks: List[str], vectors: List[List[float]]):
        """Batch-adds document chunks with their vectors to Weaviate."""
        with self.client.batch as batch:
            for i, chunk_text in enumerate(chunks):
                data_object = {
                    "document_id": document_id,
                    "filename": filename,
                    "content": chunk_text,
                }
                batch.add_data_object(
                    data_object,
                    class_name=WEAVIATE_CLASS_NAME,
                    vector=vectors[i],
                    uuid=uuid.uuid4()
                )
        logger.info(f"Added {len(chunks)} chunks for document_id {document_id} to Weaviate.")

    def semantic_search(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Performs semantic search using a query vector."""
        near_vector = {"vector": query_vector}

        result = (
            self.client.query
            .get(WEAVIATE_CLASS_NAME, ["content", "document_id"])
            .with_near_vector(near_vector)
            .with_limit(top_k)
            .with_additional(["distance"])
            .do()
        )

        return result["data"]["Get"][WEAVIATE_CLASS_NAME]
