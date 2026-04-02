"""
User and UserSettings SQLAlchemy models for authentication and authorization.
Based on the ApexAcquisitions database schema specification.

Uses String-based columns for enum fields so models work with both
PostgreSQL (production) and SQLite (development).  The PostgreSQL migration
(migrations/001_create_user_auth_tables.sql) creates proper ENUM types.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.models.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False)  # wholesaler | investor | admin
    subscription_tier = Column(String(20), nullable=True)  # starter | pro | enterprise
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(20), nullable=True)  # active | past_due | canceled | trialing
    subscription_expires_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    settings = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    notification_email = Column(Boolean, default=True, nullable=False)
    notification_sms = Column(Boolean, default=False, nullable=False)
    notification_investor_match = Column(Boolean, default=True, nullable=False)
    default_search_radius_miles = Column(Integer, default=50, nullable=False)
    timezone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id}>"
