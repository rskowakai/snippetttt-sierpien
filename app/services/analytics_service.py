from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass

from app.models import User, Document, Query, Subscription, DocumentStatus

@dataclass
class UsageMetrics:
    total_users: int
    active_users: int
    new_users: int
    total_documents: int
    documents_processed: int
    total_queries: int

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_usage_metrics(self, period_days: int = 30) -> UsageMetrics:
        """Get comprehensive usage metrics"""
        start_date = datetime.utcnow() - timedelta(days=period_days)

        total_users = self.db.query(func.count(User.id)).scalar()

        active_users = self.db.query(func.count(User.id)).filter(
            User.last_login_at >= start_date
        ).scalar()

        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= start_date
        ).scalar()

        total_documents = self.db.query(func.count(Document.id)).scalar()

        documents_processed = self.db.query(func.count(Document.id)).filter(
            Document.status == DocumentStatus.PROCESSED,
            Document.processed_at >= start_date
        ).scalar()

        total_queries = self.db.query(func.count(Query.id)).filter(
            Query.created_at >= start_date
        ).scalar()

        return UsageMetrics(
            total_users=total_users,
            active_users=active_users,
            new_users=new_users,
            total_documents=total_documents,
            documents_processed=documents_processed,
            total_queries=total_queries
        )

    async def generate_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized insights for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        total_docs = self.db.query(func.count(Document.id)).filter(Document.owner_id == user.id).scalar()
        total_queries = self.db.query(func.count(Query.id)).filter(Query.user_id == user.id).scalar()

        return {
            "total_documents": total_docs,
            "total_queries": total_queries,
            "member_since": user.created_at.isoformat()
        }
