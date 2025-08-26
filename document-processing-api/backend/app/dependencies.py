from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, models
from .core.security import ALGORITHM
from .config import settings
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.user.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception

    # In a real app, you would fetch the user from the database
    # For now, we'll create a placeholder user object
    from .models.user import User, UserRole
    import uuid

    # This is a placeholder. A real implementation would fetch from DB.
    # user = await user_repo.get_user_by_email(db, email=token_data.email)
    user = User(id=uuid.uuid4(), email=token_data.email, role=UserRole.USER, password_hash="fake_hash")

    if not user:
        raise credentials_exception
    return user
