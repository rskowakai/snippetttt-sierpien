from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import opcja_service
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/opcje", tags=["Opcje"])

@router.post("/{opcja_id}/kup")
async def purchase_opcja(
    opcja_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'CLIENT':
        raise HTTPException(status_code=403, detail='Tylko klienci mogą kupować opcje')

    try:
        await opcja_service.buy_opcja(db, opcja_id=opcja_id, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "success", "message": "Opcja została zakupiona."}
