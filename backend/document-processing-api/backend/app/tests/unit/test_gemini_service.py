import pytest
from unittest.mock import patch, MagicMock
from ...services.gemini_service import GeminiService

@patch('google.generativeai.GenerativeModel')
def test_generate_summary_success(mock_generative_model):
    """
    Unit test for GeminiService, mocking the external API call.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "This is a mock summary."
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model.return_value = mock_model_instance

    gemini_service = GeminiService(api_key="fake-key", model_name="fake-model")

    # Act
    summary = gemini_service.generate_summary("This is a long document text.")

    # Assert
    assert summary == "This is a mock summary."
    mock_model_instance.generate_content.assert_called_once()
    # Check if the prompt is correctly formatted
    call_args = mock_model_instance.generate_content.call_args
    assert "Summarize the following document" in call_args[0][0]
    assert "This is a long document text." in call_args[0][0]

def test_generate_summary_empty_text():
    """
    Test that an empty summary is returned for empty input text.
    """
    gemini_service = GeminiService(api_key="fake-key", model_name="fake-model")
    summary = gemini_service.generate_summary("   ")
    assert summary == ""
