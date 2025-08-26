from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
import redis

router = APIRouter()

@router.get("/", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Checks connections to the database and Redis.
    """
    try:
        # Check DB connection
        await db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    try:
        # Check Redis connection
        from ..services.cache_service import cache_service
        await cache_service.redis_client.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    return {"database_status": db_status, "redis_status": redis_status}
