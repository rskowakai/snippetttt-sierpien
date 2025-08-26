from fastapi import FastAPI
from .config import settings
from .api import health, documents, search
from .services.vector_service import VectorService
from prometheus_fastapi_instrumentator import Instrumentator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- Monitoring ---
# Instrumentator().instrument(app).expose(app)

# --- API Routers ---
app.include_router(health.router, prefix="/health")
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents")
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search")

@app.on_event("startup")
async def startup_event():
    """
    On startup, initialize the Weaviate schema.
    """
    logger.info("Application startup...")
    try:
        vector_service = VectorService(url=settings.WEAVIATE_URL, api_key=settings.WEAVIATE_API_KEY)
        vector_service.initialize_schema()
    except Exception as e:
        logger.error(f"Could not initialize Weaviate schema: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
