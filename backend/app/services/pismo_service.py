from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pismo_repository import pismo_repository
from app.schemas.pismo_schema import PismoCreate
from app.models.user import User

async def create_pismo(db: AsyncSession, data: PismoCreate, user: User):
    # Walidacja roli
    if user.role != "CLIENT":
        raise PermissionError("Tylko klient może złożyć pismo")

    pismo_data = data.model_dump()
    pismo_data['owner_id'] = user.id

    # In a real repo layer, we would pass the db session. This is simplified.
    return await pismo_repository.create(db, obj_in=pismo_data)

async def get_pismo_by_id(db: AsyncSession, pismo_id: int, user: User):
    pismo = await pismo_repository.get(db, pismo_id)
    if not pismo:
        raise ValueError("Pismo nie istnieje")
    # Kontrola dostępu
    if user.role == "CLIENT" and pismo.owner_id != user.id:
        raise PermissionError("Brak dostępu")
    return pismo

async def list_pisma_for_user(db: AsyncSession, user: User):
    if user.role == "ADMIN":
        return await pismo_repository.get_all(db)
    return await pismo_repository.list_by_owner(db, owner_id=user.id)
