"""
Voice / TwiML Service
Builds Twilio Markup Language (TwiML) responses that control the phone call.

Voice used: Amazon Polly "Joanna" – a natural-sounding American English female voice
available through Twilio at no extra cost.
"""

from xml.etree.ElementTree import Element, SubElement, tostring, indent

from app.config import settings

# Twilio voice identifier – Polly.Joanna is a natural-sounding female voice
MAKAYLA_VOICE = "Polly.Joanna"

# How many seconds of silence before Twilio considers the caller done speaking
SPEECH_TIMEOUT = "auto"


def _twiml_str(response_el: Element) -> str:
    """Serialise an XML element to a UTF-8 TwiML string."""
    indent(response_el)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        response_el, encoding="unicode"
    )


# ──────────────────────────────────────────────
# TwiML builders
# ──────────────────────────────────────────────

def twiml_greeting(message: str) -> str:
    """
    Play Makayla's greeting then immediately begin listening.
    Twilio will POST the transcription to /voice/gather.
    """
    response = Element("Response")

    gather = SubElement(
        response,
        "Gather",
        attrib={
            "input": "speech",
            "action": f"{settings.base_url}/voice/gather",
            "method": "POST",
            "speechTimeout": SPEECH_TIMEOUT,
            "language": "en-US",
            "speechModel": "phone_call",
        },
    )
    say = SubElement(gather, "Say", attrib={"voice": MAKAYLA_VOICE})
    say.text = message

    # Fallback if caller says nothing
    redirect = SubElement(response, "Redirect")
    redirect.text = f"{settings.base_url}/voice/no-input"

    return _twiml_str(response)


def twiml_respond_and_listen(message: str, call_sid: str) -> str:
    """
    Speak Makayla's response then listen for the next caller utterance.
    """
    response = Element("Response")

    gather = SubElement(
        response,
        "Gather",
        attrib={
            "input": "speech",
            "action": f"{settings.base_url}/voice/gather",
            "method": "POST",
            "speechTimeout": SPEECH_TIMEOUT,
            "language": "en-US",
            "speechModel": "phone_call",
        },
    )
    say = SubElement(gather, "Say", attrib={"voice": MAKAYLA_VOICE})
    say.text = message

    # Fallback if caller goes silent for too long
    redirect = SubElement(response, "Redirect")
    redirect.text = f"{settings.base_url}/voice/no-input"

    return _twiml_str(response)


def twiml_end_call(message: str) -> str:
    """
    Speak a closing message then hang up.
    """
    response = Element("Response")

    say = SubElement(response, "Say", attrib={"voice": MAKAYLA_VOICE})
    say.text = message

    SubElement(response, "Hangup")

    return _twiml_str(response)


def twiml_transfer_to_human(message: str, forward_to: str | None = None) -> str:
    """
    Tell the caller they're being transferred, then dial the shop's main line.
    Falls back to a plain hang-up if no forward number is configured.
    """
    forward_number = forward_to or settings.business_phone
    response = Element("Response")

    say = SubElement(response, "Say", attrib={"voice": MAKAYLA_VOICE})
    say.text = message

    # Only attempt dial if we have a real E.164 phone number
    if forward_number and forward_number.startswith("+"):
        dial = SubElement(response, "Dial")
        number = SubElement(dial, "Number")
        number.text = forward_number
    else:
        say2 = SubElement(response, "Say", attrib={"voice": MAKAYLA_VOICE})
        say2.text = (
            f"Our number is {settings.business_phone}. "
            "Thank you for calling, and have a great day!"
        )
        SubElement(response, "Hangup")

    return _twiml_str(response)


def twiml_no_input() -> str:
    """
    Response when the caller stays silent – prompt them once then hang up.
    """
    response = Element("Response")

    gather = SubElement(
        response,
        "Gather",
        attrib={
            "input": "speech",
            "action": f"{settings.base_url}/voice/gather",
            "method": "POST",
            "speechTimeout": SPEECH_TIMEOUT,
            "language": "en-US",
        },
    )
    say = SubElement(gather, "Say", attrib={"voice": MAKAYLA_VOICE})
    say.text = (
        "I'm sorry, I didn't hear you. Are you still there? "
        "Please go ahead whenever you're ready."
    )

    # If still nothing – goodbye
    say2 = SubElement(response, "Say", attrib={"voice": MAKAYLA_VOICE})
    say2.text = (
        f"Thank you for calling {settings.business_name}. "
        "Feel free to call us back anytime. Have a great day!"
    )
    SubElement(response, "Hangup")

    return _twiml_str(response)
