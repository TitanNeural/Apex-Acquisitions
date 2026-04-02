"""
Pydantic schemas for user authentication request/response validation.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    role: str = Field(..., pattern="^(wholesaler|investor|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)


class UserSettingsUpdate(BaseModel):
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    notification_investor_match: Optional[bool] = None
    default_search_radius_miles: Optional[int] = Field(None, ge=1, le=500)
    timezone: Optional[str] = Field(None, max_length=50)


# --- Response Schemas ---


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    company_name: Optional[str]
    role: str
    subscription_tier: Optional[str]
    subscription_status: Optional[str]
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    notification_email: bool
    notification_sms: bool
    notification_investor_match: bool
    default_search_radius_miles: int
    timezone: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
