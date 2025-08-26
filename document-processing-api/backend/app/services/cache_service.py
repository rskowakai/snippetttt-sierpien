import redis.asyncio as redis
from ..config import settings
import json
from typing import Any, Optional

class CacheService:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        """
        value = await self.redis_client.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, expire: int = 3600):
        """
        Set a value in the cache with an expiration time.
        """
        await self.redis_client.set(key, json.dumps(value), ex=expire)

    async def delete(self, key: str):
        """
        Delete a value from the cache.
        """
        await self.redis_client.delete(key)

# Singleton instance for caching
cache_service = CacheService(redis_url=settings.REDIS_CACHE_URL)
