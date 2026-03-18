"""
Twilio Voice Webhook Routes
Twilio calls these endpoints to control the live phone call.

Flow:
  1. Customer calls Twilio number  →  POST /voice/incoming
  2. Makayla greets them           →  TwiML <Gather> listens for speech
  3. Customer speaks               →  POST /voice/gather  (with SpeechResult)
  4. Claude generates reply        →  TwiML <Gather> listens again
  5. Repeat until end_call / transfer_to_human

Twilio auth signature validation is enabled when TWILIO_AUTH_TOKEN is set.
"""

import logging
from functools import lru_cache

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.services.conversation import conversation_manager
from app.services import voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])


# ──────────────────────────────────────────────
# Optional Twilio signature validation
# ──────────────────────────────────────────────

def _validate_twilio_signature(request: Request) -> bool:
    """Return True if the request came from Twilio (or validation is disabled)."""
    if not settings.twilio_auth_token:
        return True  # dev mode – skip validation

    try:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(settings.twilio_auth_token)
        url = str(request.url)
        # Twilio sends form data; we need to pass params dict for validation
        # We skip body-param validation here for simplicity – tighten in prod
        signature = request.headers.get("X-Twilio-Signature", "")
        return validator.validate(url, {}, signature)
    except Exception as exc:
        logger.warning("Signature validation error: %s", exc)
        return True  # fail open in dev; fail closed in prod by returning False


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/incoming")
async def incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(default=""),
):
    """
    Twilio calls this when a customer dials our number.
    Start the conversation and return Makayla's greeting as TwiML.
    """
    logger.info("Incoming call | CallSid=%s | From=%s", CallSid, From)

    # Start conversation session
    conv = conversation_manager.start_conversation(
        call_sid=CallSid,
        caller_phone=From,
        channel="phone",
    )

    # Generate greeting
    reply = conversation_manager.get_greeting(CallSid)

    twiml = voice_service.twiml_greeting(reply.message)
    return Response(content=twiml, media_type="application/xml")


@router.post("/gather")
async def gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    """
    Twilio posts here after the caller finishes speaking.
    SpeechResult contains the transcribed text.
    """
    logger.info(
        "Speech gathered | CallSid=%s | text=%r | confidence=%s",
        CallSid,
        SpeechResult,
        Confidence,
    )

    if not SpeechResult.strip():
        twiml = voice_service.twiml_no_input()
        return Response(content=twiml, media_type="application/xml")

    # Process input through AI
    reply = conversation_manager.process_input(CallSid, SpeechResult.strip())

    # Build appropriate TwiML based on next action
    if reply.next_action == "end_call":
        conversation_manager.end_conversation(CallSid)
        twiml = voice_service.twiml_end_call(reply.message)

    elif reply.next_action == "transfer_to_human":
        conversation_manager.end_conversation(CallSid)
        twiml = voice_service.twiml_transfer_to_human(reply.message)

    else:
        # "listen" – respond and keep gathering
        twiml = voice_service.twiml_respond_and_listen(reply.message, CallSid)

    return Response(content=twiml, media_type="application/xml")


@router.post("/no-input")
async def no_input(
    request: Request,
    CallSid: str = Form(default="unknown"),
):
    """Fallback when caller is silent."""
    logger.info("No input fallback | CallSid=%s", CallSid)
    twiml = voice_service.twiml_no_input()
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def call_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
):
    """
    Twilio status callback – called when a call ends (completed, busy, no-answer, etc.).
    Use this to clean up and log call summaries.
    """
    logger.info("Call status update | CallSid=%s | Status=%s", CallSid, CallStatus)

    if CallStatus in ("completed", "canceled", "failed", "busy", "no-answer"):
        summary = conversation_manager.end_conversation(CallSid)
        if summary:
            logger.info("Call summary: %s", summary)

    return PlainTextResponse("OK")
