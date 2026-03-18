"""
REST API Routes
- Admin dashboard data endpoints
- Text-based chat endpoint (for web widget / testing)
- Webhook for SMS (optional extension)
"""

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation import conversation_manager
from app.services.ai_service import generate_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["API"])

import os
_template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=_template_dir)


# ──────────────────────────────────────────────
# Dashboard (served from templates/index.html)
# ──────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard(request: Request):
    """Admin dashboard showing active and recent conversations."""
    convs = conversation_manager.get_all_conversations()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "conversations": convs,
            "business_name": settings.business_name,
            "receptionist_name": settings.receptionist_name,
            "total": len(convs),
        },
    )


# ──────────────────────────────────────────────
# Conversations
# ──────────────────────────────────────────────

@router.get("/conversations")
def list_conversations():
    """Return summary list of all conversations (active + ended)."""
    return {"conversations": conversation_manager.get_all_conversations()}


@router.get("/conversations/{call_sid}")
def get_conversation(call_sid: str):
    """Return full detail (including message history) for a single call."""
    detail = conversation_manager.get_conversation_detail(call_sid)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return detail


# ──────────────────────────────────────────────
# Text-based chat (web widget / Postman testing)
# ──────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """
    Simulate a conversation turn over text (no phone required).
    Useful for testing Makayla's responses without a Twilio setup.

    - If call_sid is omitted a new session is created automatically.
    - If call_sid is provided the conversation continues from where it left off.
    """
    call_sid = payload.call_sid or f"web_{payload.session_id or 'anon'}"

    # Create session if new
    if not conversation_manager.get_conversation(call_sid):
        conversation_manager.start_conversation(
            call_sid=call_sid,
            caller_phone=payload.caller_phone or "web",
            channel="web",
        )
        # First turn – give greeting
        if not payload.message:
            reply = conversation_manager.get_greeting(call_sid)
            return ChatResponse(
                call_sid=call_sid,
                message=reply.message,
                next_action=reply.next_action,
                customer_data={},
            )

    if not payload.message:
        raise HTTPException(status_code=400, detail="message is required for ongoing sessions")

    reply = conversation_manager.process_input(call_sid, payload.message)
    conv = conversation_manager.get_conversation(call_sid)

    return ChatResponse(
        call_sid=call_sid,
        message=reply.message,
        next_action=reply.next_action,
        customer_data=conv.customer_data if conv else {},
    )
