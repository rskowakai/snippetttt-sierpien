from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from typing import Optional, List
from enum import Enum
import os
from pathlib import Path

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PrawoAsystent AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI Legal Document Assistant"

    # Security
    SECRET_KEY: str = "default_secret_key_that_is_long_enough_to_pass_validation"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/prawoasystent"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis & Caching
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600
    RATE_LIMIT_PER_MINUTE: int = 60

    # File Storage
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".mp3", ".wav", ".mp4"]
    GOOGLE_CLOUD_PROJECT: str = "test-project"
    GOOGLE_CLOUD_STORAGE_BUCKET: str = "test-bucket"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # AI Services
    GEMINI_API_KEY: str = "test-gemini-key"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL_TIMEOUT_SECONDS: int = 60
    MAX_TOKENS_PER_REQUEST: int = 4000

    # Vector Database
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    VECTOR_DIMENSION: int = 768
    SIMILARITY_THRESHOLD: float = 0.7

    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_DOCUMENT: int = 1000
    OCR_ENABLED: bool = True

    # Subscription Plans
    FREE_PLAN_DOCS: int = 5
    FREE_PLAN_QUERIES: int = 100
    BASIC_PLAN_DOCS: int = 50
    BASIC_PLAN_QUERIES: int = 1000
    PREMIUM_PLAN_DOCS: int = 200
    PREMIUM_PLAN_QUERIES: int = 5000

    # Payment
    STRIPE_SECRET_KEY: str = "sk_test_123"
    STRIPE_WEBHOOK_SECRET: str = "whsec_test_123"
    STRIPE_PRICE_BASIC_MONTHLY: str = "price_basic_monthly"
    STRIPE_PRICE_PREMIUM_MONTHLY: str = "price_premium_monthly"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    METRICS_ENABLED: bool = True

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@prawoasystent.ai"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

settings = Settings()
