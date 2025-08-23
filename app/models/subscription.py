from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel
from .enums import SubscriptionPlan, SubscriptionStatus

class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)

    stripe_subscription_id = Column(String(255), unique=True)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="subscription")
