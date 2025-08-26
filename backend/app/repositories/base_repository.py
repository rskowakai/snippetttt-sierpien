from typing import Generic, TypeVar, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import Base, get_db

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        statement = select(self.model).where(self.model.id == id)
        results = await db.execute(statement)
        return results.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> list[ModelType]:
        statement = select(self.model)
        results = await db.execute(statement)
        return results.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
