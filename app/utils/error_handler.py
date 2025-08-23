import asyncio
import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union

import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    # Simplified for stub
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

@dataclass
class ErrorResponse:
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None

class PrawoAsystentException(Exception):
    """Base exception for the application"""
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
        self.retry_after = retry_after
        super().__init__(message)

class ErrorHandler:
    @staticmethod
    @retry(
        retry=tenacity.retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def with_retry(func, *args, **kwargs):
        return await func(*args, **kwargs)

    @staticmethod
    async def handle_ai_service_error(error: Exception) -> str:
        if "rate_limit" in str(error).lower():
            return "Osiągnięto limit zapytań. Spróbuj ponownie za chwilę."
        else:
            return "Wystąpił błąd podczas przetwarzania. Skontaktuj się z supportem."


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Union[Exception, tuple] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise PrawoAsystentException(
                    ErrorCode.SERVICE_UNAVAILABLE, "Service temporarily unavailable"
                )

        try:
            result = await func(*args, **kwargs)
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
            raise e

class ResilientService:
    # This is a conceptual placeholder. A full implementation would be more complex.
    def __init__(self, name: str, circuit_breaker: Optional[CircuitBreaker] = None):
        self.name = name
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.logger = logging.getLogger(f"resilient.{name}")
