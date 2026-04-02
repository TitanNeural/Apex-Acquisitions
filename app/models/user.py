"""
User and UserSettings SQLAlchemy models for authentication and authorization.
Based on the ApexAcquisitions database schema specification.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    role = Column(
        Enum("wholesaler", "investor", "admin", name="user_role"),
        nullable=False,
    )
    subscription_tier = Column(
        Enum("starter", "pro", "enterprise", name="subscription_tier"),
        nullable=True,
    )
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(
        Enum("active", "past_due", "canceled", "trialing", name="subscription_status"),
        nullable=True,
    )
    subscription_expires_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    settings = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    notification_email = Column(Boolean, default=True, nullable=False)
    notification_sms = Column(Boolean, default=False, nullable=False)
    notification_investor_match = Column(Boolean, default=True, nullable=False)
    default_search_radius_miles = Column(Integer, default=50, nullable=False)
    timezone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id}>"
