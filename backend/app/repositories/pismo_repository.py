from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pismo import Pismo
from .base_repository import BaseRepository

class PismoRepository(BaseRepository[Pismo]):
    def __init__(self):
        super().__init__(Pismo)

    async def list_by_owner(self, db: AsyncSession, owner_id: int) -> list[Pismo]:
        statement = select(self.model).where(self.model.owner_id == owner_id)
        results = await db.execute(statement)
        return results.scalars().all()

pismo_repository = PismoRepository()
