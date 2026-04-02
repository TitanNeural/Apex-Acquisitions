"""
Conversation routes - lead intake endpoints.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.conversation import ConversationManager

router = APIRouter()
manager = ConversationManager()


class StartRequest(BaseModel):
    caller_phone: str
    caller_name: Optional[str] = None
    channel: str = "web"


class MessageRequest(BaseModel):
    call_id: str
    message: str


class ConversationOut(BaseModel):
    conversation_id: str
    call_id: str
    greeting: str


class MessageOut(BaseModel):
    message: str
    next_action: str
    state: str
    requires_human_handoff: bool = False
    extracted_data: dict = {}


@router.post("/start", response_model=ConversationOut)
def start_conversation(data: StartRequest):
    import uuid

    call_id = str(uuid.uuid4())[:8]
    conv = manager.start_conversation(
        call_id=call_id,
        caller_phone=data.caller_phone,
        caller_name=data.caller_name,
        channel=data.channel,
    )
    greeting = manager.get_greeting(conv.id)
    return ConversationOut(
        conversation_id=conv.id,
        call_id=call_id,
        greeting=greeting.message,
    )


@router.post("/message", response_model=MessageOut)
def send_message(data: MessageRequest):
    response = manager.process_response(
        call_id=data.call_id,
        user_input=data.message,
        input_type="text",
    )
    if response.state.value == "ended" and response.next_action == "end_call":
        raise HTTPException(status_code=404, detail="Conversation not found")
    return MessageOut(
        message=response.message,
        next_action=response.next_action,
        state=response.state.value,
        requires_human_handoff=response.requires_human_handoff,
        extracted_data=response.extracted_data,
    )


@router.post("/end")
def end_conversation(call_id: str):
    summary = manager.end_conversation(call_id)
    if summary.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Conversation not found")
    return summary


@router.get("/status/{call_id}")
def get_status(call_id: str):
    status = manager.get_conversation_status(call_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return status
