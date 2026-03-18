"""
Claude AI Service
Generates Makayla's responses using Anthropic's Claude API.
"""

import json
import logging
from typing import Any

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# System prompt – Makayla's personality & rules
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are Makayla, a friendly, warm, and professional AI receptionist \
for {business_name}, an automotive service shop.

BUSINESS INFO:
- Name: {business_name}
- Phone: {business_phone}
- Address: {business_address}
- Hours: {business_hours}

YOUR JOB:
1. Greet callers warmly and make them feel welcome.
2. Collect the following information one step at a time (never all at once):
   a. Customer's first name
   b. Best callback phone number (if we don't already have it)
   c. Vehicle – year, make, and model
   d. Service need or concern
3. Offer to schedule an appointment and confirm a date and time.
4. Answer general questions about services, hours, or location.
5. If something is outside your knowledge, offer to have a technician call them back.

SERVICES WE OFFER (mention relevant ones when appropriate):
- Oil changes & fluid services
- Brake inspection & repair
- Tire sales, mounting, balancing & rotation
- Wheel alignment
- Check engine / dashboard warning lights
- Battery testing & replacement
- Suspension & steering
- Scheduled maintenance

PERSONALITY GUIDELINES:
- You are on a PHONE CALL – keep responses SHORT and conversational (1-3 sentences max).
- Speak naturally, like a real person. Avoid robotic lists on the phone.
- Be warm, patient, and reassuring—especially when callers are stressed about their vehicle.
- Never say you're an AI unless directly and sincerely asked. If asked, you may say: \
"I'm Makayla, the virtual receptionist for {business_name}."
- Do NOT repeat the same phrase twice in a row.
- End EVERY response with either a question to advance the conversation OR a clear next step.

DATA EXTRACTION (internal use):
After generating your spoken response, you MUST also output a JSON block on its own line \
(never spoken aloud) in this exact format so the system can track progress:
<DATA>
{{
  "extracted": {{
    "name": null,
    "phone": null,
    "vehicle": null,
    "service_issue": null,
    "appointment_date": null,
    "appointment_time": null
  }},
  "next_action": "listen",
  "requires_human_handoff": false,
  "end_call": false
}}
</DATA>

Fill in any fields you just learned. Use null for unknown fields. next_action must be \
one of: "listen", "end_call", "transfer_to_human".
Set end_call=true ONLY after appointment is confirmed and caller has no more questions.
Set requires_human_handoff=true if the caller is very upset or has a complex technical question.
"""


def _build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(
        business_name=settings.business_name,
        business_phone=settings.business_phone,
        business_address=settings.business_address,
        business_hours=settings.business_hours,
    )


def _parse_ai_output(raw: str) -> dict[str, Any]:
    """Split Makayla's spoken text from the hidden <DATA> JSON block."""
    spoken = raw
    data: dict[str, Any] = {
        "extracted": {},
        "next_action": "listen",
        "requires_human_handoff": False,
        "end_call": False,
    }

    if "<DATA>" in raw and "</DATA>" in raw:
        parts = raw.split("<DATA>")
        spoken = parts[0].strip()
        json_part = parts[1].split("</DATA>")[0].strip()
        try:
            parsed = json.loads(json_part)
            data.update(parsed)
        except json.JSONDecodeError:
            logger.warning("Could not parse AI DATA block: %s", json_part)

    return {"message": spoken, **data}


# ──────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────
def generate_response(
    conversation_history: list[dict],
    current_customer_data: dict | None = None,
) -> dict[str, Any]:
    """
    Call Claude and return a dict with:
      - message: str            – what Makayla says aloud
      - extracted: dict         – newly extracted customer data fields
      - next_action: str        – "listen" | "end_call" | "transfer_to_human"
      - requires_human_handoff: bool
      - end_call: bool
    """
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set – using fallback response")
        return {
            "message": (
                f"Thank you for calling {settings.business_name}! "
                f"This is {settings.receptionist_name}. How can I help you today?"
            ),
            "extracted": {},
            "next_action": "listen",
            "requires_human_handoff": False,
            "end_call": False,
        }

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Prepend a context note about what we already know
    system = _build_system_prompt()
    if current_customer_data:
        known = {k: v for k, v in current_customer_data.items() if v}
        if known:
            system += f"\n\nINFO ALREADY COLLECTED: {json.dumps(known)}"

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system,
            messages=conversation_history,
        )
        raw = response.content[0].text
        logger.debug("Claude raw output: %s", raw)
        return _parse_ai_output(raw)

    except anthropic.APIError as exc:
        logger.error("Claude API error: %s", exc)
        return {
            "message": (
                "I'm so sorry, I'm having a little trouble right now. "
                "Could you hold for just a moment while I get that sorted out?"
            ),
            "extracted": {},
            "next_action": "listen",
            "requires_human_handoff": False,
            "end_call": False,
        }


def generate_greeting() -> dict[str, Any]:
    """Generate Makayla's opening line for a new call."""
    history = [
        {
            "role": "user",
            "content": "[SYSTEM: A new customer call has just connected. Greet them.]",
        }
    ]
    return generate_response(history)
