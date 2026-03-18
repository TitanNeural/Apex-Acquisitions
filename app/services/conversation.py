"""
Conversation Manager
Orchestrates the full lifecycle of a customer call:
  - Tracks conversation history per call
  - Calls the Claude AI service for responses
  - Merges extracted customer data across turns
  - Decides next TwiML action
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from app.services import ai_service

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Domain types
# ──────────────────────────────────────────────

class ConversationState(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    TRANSFERRED = "transferred"


@dataclass
class Conversation:
    """Single phone-call session."""
    id: str
    call_sid: str                       # Twilio CallSid
    caller_phone: str
    channel: str = "phone"              # phone | sms | web
    state: ConversationState = ConversationState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Full message history in Claude message format: [{"role": "user"|"assistant", "content": str}]
    history: List[Dict] = field(default_factory=list)

    # Structured data collected so far
    customer_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "call_sid": self.call_sid,
            "caller_phone": self.caller_phone,
            "channel": self.channel,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "turns": len([m for m in self.history if m["role"] == "user"]),
            "customer_data": self.customer_data,
        }


@dataclass
class ConversationResponse:
    """What the route handler needs to build the TwiML reply."""
    message: str
    next_action: str                    # "listen" | "end_call" | "transfer_to_human"
    state: ConversationState
    requires_human_handoff: bool = False
    extracted_data: Dict = field(default_factory=dict)


# ──────────────────────────────────────────────
# Manager
# ──────────────────────────────────────────────

class ConversationManager:
    """
    In-memory store of active conversations.
    One instance is shared across all requests (singleton via dependency injection).
    For production, replace the dict with Redis or a DB.
    """

    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}   # keyed by call_sid
        self.receptionist_name = "Makayla"

    # ── lifecycle ──────────────────────────────

    def start_conversation(
        self,
        call_sid: str,
        caller_phone: str,
        channel: str = "phone",
    ) -> Conversation:
        conv = Conversation(
            id=f"conv_{uuid.uuid4().hex[:8]}",
            call_sid=call_sid,
            caller_phone=caller_phone,
            channel=channel,
        )
        self._conversations[call_sid] = conv
        logger.info("New conversation started: %s | caller=%s", conv.id, caller_phone)
        return conv

    def get_conversation(self, call_sid: str) -> Optional[Conversation]:
        return self._conversations.get(call_sid)

    def end_conversation(self, call_sid: str) -> Optional[dict]:
        conv = self._conversations.get(call_sid)
        if not conv:
            return None
        conv.state = ConversationState.ENDED
        conv.updated_at = datetime.now()
        summary = {
            "call_sid": call_sid,
            "conversation_id": conv.id,
            "duration_seconds": (conv.updated_at - conv.created_at).total_seconds(),
            "customer_data": conv.customer_data,
            "turns": len([m for m in conv.history if m["role"] == "user"]),
            "status": "ended",
        }
        logger.info("Conversation ended: %s | data=%s", conv.id, conv.customer_data)
        return summary

    # ── core interaction ───────────────────────

    def get_greeting(self, call_sid: str) -> ConversationResponse:
        """
        Generate Makayla's opening line for a brand-new call.
        """
        conv = self._conversations.get(call_sid)
        if not conv:
            return self._error_response()

        ai_result = ai_service.generate_greeting()
        message = ai_result["message"]

        # Store assistant turn in history
        conv.history.append({"role": "assistant", "content": message})
        conv.updated_at = datetime.now()

        return ConversationResponse(
            message=message,
            next_action="listen",
            state=conv.state,
        )

    def process_input(self, call_sid: str, user_text: str) -> ConversationResponse:
        """
        Process what the caller just said and generate Makayla's reply.
        """
        conv = self._conversations.get(call_sid)
        if not conv:
            return self._error_response()

        if conv.state != ConversationState.ACTIVE:
            return ConversationResponse(
                message="Thank you for calling. Have a great day!",
                next_action="end_call",
                state=conv.state,
            )

        # Append caller turn
        conv.history.append({"role": "user", "content": user_text})

        # Ask Claude for a response
        ai_result = ai_service.generate_response(
            conversation_history=conv.history,
            current_customer_data=conv.customer_data,
        )

        message = ai_result.get("message", "I'm sorry, could you repeat that?")
        next_action = ai_result.get("next_action", "listen")
        handoff = ai_result.get("requires_human_handoff", False)
        end_call = ai_result.get("end_call", False)
        extracted = ai_result.get("extracted", {})

        # Merge extracted fields (only non-null values)
        for key, value in extracted.items():
            if value is not None and value != "":
                conv.customer_data[key] = value

        # Append assistant turn
        conv.history.append({"role": "assistant", "content": message})
        conv.updated_at = datetime.now()

        # Resolve final action
        if handoff:
            next_action = "transfer_to_human"
            conv.state = ConversationState.TRANSFERRED
        elif end_call or next_action == "end_call":
            next_action = "end_call"
            conv.state = ConversationState.ENDED

        logger.info(
            "Turn processed: conv=%s | action=%s | data=%s",
            conv.id,
            next_action,
            conv.customer_data,
        )

        return ConversationResponse(
            message=message,
            next_action=next_action,
            state=conv.state,
            requires_human_handoff=handoff,
            extracted_data=extracted,
        )

    # ── admin helpers ──────────────────────────

    def get_all_conversations(self) -> list[dict]:
        return [c.to_dict() for c in self._conversations.values()]

    def get_conversation_detail(self, call_sid: str) -> Optional[dict]:
        conv = self._conversations.get(call_sid)
        if not conv:
            return None
        d = conv.to_dict()
        d["history"] = conv.history
        return d

    # ── internals ─────────────────────────────

    @staticmethod
    def _error_response() -> ConversationResponse:
        return ConversationResponse(
            message=(
                "I'm so sorry, I'm having trouble with your call right now. "
                "Please try calling back in just a moment."
            ),
            next_action="end_call",
            state=ConversationState.ENDED,
        )


# ──────────────────────────────────────────────
# Shared singleton
# ──────────────────────────────────────────────
conversation_manager = ConversationManager()
