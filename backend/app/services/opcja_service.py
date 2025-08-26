from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.opcja_repository import opcja_repository
from app.models.user import User

async def buy_opcja(db: AsyncSession, opcja_id: int, user: User):
    if user.role != "CLIENT":
        raise PermissionError("Tylko klient może kupować opcje")

    opcja = await opcja_repository.get(db, id=opcja_id)
    if not opcja:
        raise ValueError("Opcja nie istnieje")

    # Here you would add logic to check if the user has access to the parent Pismo,
    # and integrate with a payment provider like Stripe.

    opcja.is_purchased = True
    await db.commit()
    await db.refresh(opcja)
    return opcja
