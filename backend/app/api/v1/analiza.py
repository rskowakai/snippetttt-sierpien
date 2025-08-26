from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analiza import AnalizaCreate, AnalizaRead
from app.services import analiza_service
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/analizy", tags=["Analizy"])

@router.post("/", response_model=AnalizaRead)
async def create_new_analiza(
    payload: AnalizaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail='Tylko admin może tworzyć analizy')
    return await analiza_service.create_analiza(db, data=payload, user=current_user)
