from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models import User
from app.db.session import get_db
from app.api.dependencies import get_current_admin_user, get_current_active_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/usage", response_model=Dict[str, Any])
async def get_usage_analytics(
    period_days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system usage analytics (admin only)"""
    analytics_service = AnalyticsService(db)
    metrics = await analytics_service.get_usage_metrics(period_days)
    return metrics.__dict__

@router.get("/users/me/insights", response_model=Dict[str, Any])
async def get_user_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized user insights"""
    analytics_service = AnalyticsService(db)
    insights = await analytics_service.generate_user_insights(str(current_user.id))
    return insights
