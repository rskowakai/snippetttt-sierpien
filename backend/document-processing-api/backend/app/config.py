import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Processing API"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    # Redis
    REDIS_BROKER_URL: str
    REDIS_CACHE_URL: str

    # Weaviate
    WEAVIATE_URL: str
    WEAVIATE_API_KEY: str | None = None

    # Sentry
    SENTRY_DSN: str | None = None

    # ML Models
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    GOOGLE_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
