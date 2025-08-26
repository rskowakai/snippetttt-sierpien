from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
