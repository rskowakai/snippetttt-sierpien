from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core
    PROJECT_NAME: str = "Document Processing API"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Weaviate
    WEAVIATE_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
