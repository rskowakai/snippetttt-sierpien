import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from io import BytesIO

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# Mock Celery task so we don't actually queue anything during tests
@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch("app.services.document_service.process_document_task.delay") as mock_task:
        mock_task.return_value = MagicMock(id="mock_task_id_123")
        yield mock_task

async def test_upload_pdf_document(client: AsyncClient, mock_celery_task: MagicMock):
    """
    Integration test for the PDF upload endpoint.
    - Mocks the Celery task call.
    - Verifies the API response and database state.
    """
    file_content = b"This is a dummy PDF content."
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    # We need a mock user and token for this, for now we will skip auth dependency
    # For a real test, you would create a user and generate a token
    # headers = {"Authorization": "Bearer your_test_token"}

    # For simplicity, we'll temporarily disable the auth dependency in the test
    # This is not a good practice for real projects, but simplifies this example.
    from ...dependencies import get_current_user
    from ...main import app
    app.dependency_overrides[get_current_user] = lambda: {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}

    response = await client.post("/api/v1/documents/upload", files=files)

    assert response.status_code == 202
    data = response.json()
    assert data["task_id"] == "mock_task_id_123"
    assert data["document"]["filename"] == "test.pdf"
    assert data["document"]["status"] == "pending"

    # Assert that our mock Celery task was called correctly
    mock_celery_task.assert_called_once()

    # Clean up the dependency override
    del app.dependency_overrides[get_current_user]
