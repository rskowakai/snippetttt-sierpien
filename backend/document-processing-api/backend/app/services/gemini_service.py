import google.generativeai as genai
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("Google API Key is not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Gemini Service initialized with model: {model_name}")

    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """
        Generates a summary for the given text using the Gemini model.
        """
        if not text.strip():
            return ""

        prompt = f"Summarize the following document in about {max_length} words. Provide a concise and informative summary that captures the main points. Document text: \n\n{text}"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating summary with Gemini: {e}")
            return f"Could not generate summary. Error: {e}"

# Singleton instance
gemini_service = GeminiService(api_key=settings.GOOGLE_API_KEY, model_name=settings.GEMINI_MODEL_NAME)
