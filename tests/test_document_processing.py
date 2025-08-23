import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.models import Document, DocumentType, DocumentStatus, Query, QueryType
from app.services.rag_service import EnhancedRAGService

class TestDocumentProcessing:

    @pytest.mark.asyncio
    async def test_document_upload_success(self, test_client, test_user, auth_headers):
        """Test successful document upload"""

        file_content = b"Test PDF content"
        files = {"file": ("test.pdf", file_content, "application/pdf")}

        # We don't have the full DocumentService, so we patch the endpoint directly
        # This is more of an integration test for the endpoint
        response = await test_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "test.pdf"
        assert data["status"] == "uploaded"

    @pytest.mark.asyncio
    async def test_document_query_success(self, test_client, test_user, auth_headers, test_db):
        """Test successful document query"""

        db = test_db()
        document = Document(
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="test/path",
            file_size=1000,
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            status=DocumentStatus.PROCESSED,
            owner_id=test_user.id,
            weaviate_id="test-weaviate-id"
        )
        db.add(document)
        db.commit()

        mock_query_result = Query(
            id="c7a748a4-3532-4752-953c-13b731997a35",
            question="Test question?",
            answer="Test answer",
            confidence_score=0.85,
            processing_time=1.5,
            query_type=QueryType.FACTUAL,
            user_id=test_user.id,
            document_id=document.id
        )

        with patch('app.api.v1.endpoints.documents.EnhancedRAGService.process_query', new_callable=AsyncMock) as mock_process_query:
            mock_process_query.return_value = mock_query_result

            response = await test_client.post(
                f"/api/v1/documents/{document.id}/query",
                json={"question": "Test question?"},
                headers=auth_headers
            )

        db.close()

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Test answer"
        assert data["confidence_score"] == 0.85
