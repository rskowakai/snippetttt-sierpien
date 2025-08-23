import logging
import time
import uvicorn
from fastapi import FastAPI, Request, Response, APIRouter
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.api.v1.endpoints import documents, health, analytics
from app.db.session import engine
from app.models import Base

# This would create tables in the database.
# For this stub, we might not want to run it automatically.
# Base.metadata.create_all(bind=engine)

# In a real app, monitoring would be more sophisticated.
# These are stubs for the classes from the prompt.
class MetricsService:
    async def record_request(self, method, endpoint, status_code, duration):
        logging.info(f"METRICS: {method} {endpoint} {status_code} {duration:.4f}s")

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics_service: MetricsService):
        super().__init__(app)
        self.metrics_service = metrics_service

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time
        await self.metrics_service.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        return response

# App initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Add middleware
metrics_service = MetricsService()
app.add_middleware(MetricsMiddleware, metrics_service=metrics_service)


# Add routers
api_router = APIRouter(prefix=settings.API_V1_PREFIX)
api_router.include_router(documents.router)
api_router.include_router(health.health_router)
api_router.include_router(analytics.router)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    logger.info("Starting up PrawoAsystent AI...")
    # In a real app, you might connect to databases, warm up caches, etc.

@app.on_event("shutdown")
async def shutdown_event():
    logger = logging.getLogger(__name__)
    logger.info("Shutting down PrawoAsystent AI...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
