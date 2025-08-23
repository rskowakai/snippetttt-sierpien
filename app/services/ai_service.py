import asyncio
import httpx
import logging
from typing import Optional

from app.core.config import settings
from app.utils.error_handler import ResilientService, CircuitBreaker, PrawoAsystentException, ErrorCode

logger = logging.getLogger(__name__)

# Stubs for adapters
class GeminiAdapter:
    async def generate_response(self, prompt: str) -> str:
        logger.info("Using GeminiAdapter")
        await asyncio.sleep(0.1) # simulate network call
        return f"Response from Gemini for: {prompt}"

class OpenAIAdapter:
    async def generate_response(self, prompt: str) -> str:
        logger.info("Using OpenAIAdapter")
        await asyncio.sleep(0.1) # simulate network call
        return f"Response from OpenAI for: {prompt}"

# Placeholder for the simpler AIService used in some parts of the code
class AIService:
    def __init__(self, settings_param=None):
        pass

    async def generate_summary(self, text: str) -> str:
        return "This is a placeholder summary."

    async def extract_legal_entities(self, text: str) -> dict:
        return {"entities": []}

    async def _generate_with_retry(self, prompt: str) -> str:
        # This is a simplified version of the retry logic.
        # The full implementation would use the ResilientService.
        try:
            # In a real scenario, this would call an AI model
            await asyncio.sleep(0.2)
            return f"Generated answer for prompt: {prompt}"
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise PrawoAsystentException(ErrorCode.AI_SERVICE_ERROR, "AI service failed")

    async def expand_query(self, question: str, context) -> list[str]:
        return [question]

    async def generate_follow_up_questions(self, question: str, answer: str, document_id: str) -> list[str]:
        return [
            "What is the next step?",
            "Can you elaborate on section 2?",
            "What are the key dates?"
        ]


# Circuit breaker for AI services
ai_service_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=120,
    expected_exception=(httpx.RequestError, asyncio.TimeoutError)
)

class EnhancedAIService(ResilientService):
    def __init__(self):
        super().__init__("ai_service", ai_service_circuit_breaker)
        self.primary_adapter = GeminiAdapter()
        self.fallback_adapter = OpenAIAdapter() if settings.OPENAI_API_KEY else None

    async def generate_response_with_fallback(self, prompt: str) -> str:
        """Generate response with fallback to secondary AI service"""

        async def primary_call():
            return await self.primary_adapter.generate_response(prompt)

        async def fallback_call():
            return await self._fallback_generate_response(prompt)

        # The with_resilience context manager is complex, so we'll simulate its logic
        try:
            # Try primary service with circuit breaker
            return await self.circuit_breaker.call(primary_call)
        except Exception as e:
            logger.warning(f"Primary AI service failed: {e}. Trying fallback.")
            if self.fallback_adapter:
                # Try fallback service
                try:
                    return await fallback_call()
                except Exception as fb_e:
                    logger.error(f"Fallback AI service also failed: {fb_e}")
                    raise PrawoAsystentException(
                        ErrorCode.AI_SERVICE_ERROR,
                        "All AI services are currently unavailable.",
                        suggestion="Please try again in a few minutes."
                    )
            else:
                # No fallback available
                raise PrawoAsystentException(
                    ErrorCode.AI_SERVICE_ERROR,
                    "Primary AI service failed and no fallback is available.",
                    suggestion="Please try again later."
                )

    async def _fallback_generate_response(self, prompt: str) -> str:
        """Fallback response generation"""
        if self.fallback_adapter:
            return await self.fallback_adapter.generate_response(prompt)
        else:
            raise PrawoAsystentException(
                ErrorCode.AI_SERVICE_ERROR,
                "AI service temporarily unavailable",
                suggestion="Please try again in a few minutes"
            )
