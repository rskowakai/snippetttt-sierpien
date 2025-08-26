from sqlalchemy.ext.asyncio import AsyncSession
from ..models.audit import AuditLog
from typing import Any, Dict, Optional
import uuid

class AuditService:
    @staticmethod
    async def create_audit_log(
        db: AsyncSession,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[uuid.UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ):
        """
        Creates an audit log entry.
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log

audit_service = AuditService()
