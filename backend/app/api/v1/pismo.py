from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pismo_schema import PismoCreate, PismoRead
from app.services import pismo_service
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/pisma", tags=["Pisma"])

@router.post("/", response_model=PismoRead)
async def submit_pismo(
    payload: PismoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'CLIENT':
        raise HTTPException(status_code=403, detail='Tylko klienci mogą składać pisma')
    return await pismo_service.create_pismo(db, data=payload, user=current_user)

@router.get("/", response_model=List[PismoRead])
async def get_pisma(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await pismo_service.list_pisma_for_user(db, user=current_user)

@router.get("/{pismo_id}", response_model=PismoRead)
async def get_pismo(
    pismo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pismo = await pismo_service.get_pismo_by_id(db, pismo_id=pismo_id, user=current_user)
    if not pismo:
        raise HTTPException(status_code=404, detail="Pismo not found")
    return pismo
