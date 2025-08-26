from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analiza_repository import analiza_repository
from app.schemas.analiza import AnalizaCreate
from app.models.user import User

async def create_analiza(db: AsyncSession, data: AnalizaCreate, user: User):
    if user.role != "ADMIN":
        raise PermissionError("Tylko admin może tworzyć analizy")

    analiza_data = data.model_dump()
    analiza_data['admin_id'] = user.id

    return await analiza_repository.create(db, obj_in=analiza_data)
