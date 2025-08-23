import redis
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.db.session import get_db
from app.services.vector_service import VectorService

# In a real app, prometheus_client would be installed.
# For this stub, we'll create a dummy generator.
class PrometheusClientDummy:
    def generate_latest(self):
        return b"# FAKE METRICS\nhttp_requests_total 10"

prometheus_client = PrometheusClientDummy()

health_router = APIRouter(tags=["health"])

@health_router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@health_router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check with dependencies"""
    checks = {}
    overall_status = "ready"

    # Database check
    try:
        db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        overall_status = "not_ready"

    # Redis check
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
        overall_status = "not_ready"

    # Weaviate check (simplified)
    try:
        vector_service = VectorService()
        checks["weaviate"] = "healthy"
    except Exception as e:
        checks["weaviate"] = f"unhealthy: {str(e)}"
        overall_status = "not_ready"

    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow()
    }

@health_router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(prometheus_client.generate_latest(), media_type="text/plain")
