import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.services.security_service import verify_token

logger = logging.getLogger(__name__)

async def get_current_user(db: Session = Depends(get_db), token: str = "dummy_token"):
    # This is a stub for user authentication.
    # In a real app, you'd use something like Depends(OAuth2PasswordBearer(tokenUrl="token"))
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_token(token)
    if user_id is None:
        # In a real app, the token verification would handle this
        # For the stub, we'll just get the first user for testing purposes
        user = db.query(User).first()
        if not user:
            # Create a dummy user if none exist
            from app.services.security_service import get_password_hash
            user = User(
                email="test@example.com",
                hashed_password=get_password_hash("test"),
                first_name="Test",
                last_name="User",
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    from app.models.enums import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

async def check_rate_limit(user_id: str, action: str):
    # Placeholder for rate limiting logic
    logger.info(f"Checking rate limit for user {user_id} performing {action}")
    pass

async def check_usage_limits(user: User, action: str, db: Session) -> bool:
    # Placeholder for usage limit logic
    logger.info(f"Checking usage limits for user {user.id} performing {action}")
    return True

def log_query_metrics(query_id: str, user_id: str, processing_time: float):
    # Placeholder for background task
    logger.info(f"Logging metrics for query {query_id} by user {user_id}. Processing time: {processing_time}s")
    pass
