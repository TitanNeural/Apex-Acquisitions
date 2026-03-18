"""
Pydantic schemas for request/response validation
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


# ──────────────────────────────────────────────
# Text / Web chat
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: Optional[str] = None
    call_sid: Optional[str] = None          # Provide to continue a session
    session_id: Optional[str] = None        # Optional friendly session label
    caller_phone: Optional[str] = "web"     # Phone number if available


class ChatResponse(BaseModel):
    call_sid: str
    message: str
    next_action: str                        # "listen" | "end_call" | "transfer_to_human"
    customer_data: Dict[str, Any] = {}


# ──────────────────────────────────────────────
# Conversation summary (returned by /api/conversations)
# ──────────────────────────────────────────────

class ConversationSummary(BaseModel):
    id: str
    call_sid: str
    caller_phone: str
    channel: str
    state: str
    created_at: str
    updated_at: str
    turns: int
    customer_data: Dict[str, Any]


# ──────────────────────────────────────────────
# Legacy – kept for backward-compat with any existing integrations
# ──────────────────────────────────────────────

class CustomerMessage(BaseModel):
    customer_name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle: Optional[str] = None
    message: str


class AIResponse(BaseModel):
    response: str
    next_step: str
