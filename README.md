AI-Receptionist/
│
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  └─ webhook.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ conversation.py
│  └─ models/
│     ├─ __init__.py
│     └─ schemas.py
│
├─ requirements.txt
├─ .env.example
└─ README.md
fastapi
uvicorn
python-dotenv
pydantic
APP_NAME=AI Receptionist
BUSINESS_NAME=EAS Tire and Auto
from fastapi import FastAPI
from dotenv import load_dotenv
import os

from app.routes.webhook import router as webhook_router

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "AI Receptionist"),
    version="1.0.0"
)

app.include_router(webhook_router)


@app.get("/")
def root():
    return {
        "message": f"{os.getenv('APP_NAME', 'AI Receptionist')} is running"
    }from pydantic import BaseModel
from typing import Optional


class CustomerMessage(BaseModel):
    customer_name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle: Optional[str] = None
    message: str


class AIResponse(BaseModel):
    response: str
    next_step: str
    import os


def generate_receptionist_response(message: str, customer_name: str | None = None) -> dict:
    """
    Simple starter conversation logic.
    Later this can be replaced with OpenAI.
    """
    business_name = os.getenv("BUSINESS_NAME", "our shop")
    msg = message.lower()

    greeting_name = customer_name if customer_name else "there"

    if any(word in msg for word in ["hello", "hi", "hey"]):
        return {
            "response": f"Thank you for calling {business_name}. This is Makayla. How can I help you today?",
            "next_step": "collect_issue"
        }

    if any(word in msg for word in ["appointment", "schedule", "book"]):
        return {
            "response": (
                f"Absolutely, {greeting_name}. I can help with that. "
                "What kind of vehicle do you have, and what would you like us to look at?"
            ),
            "next_step": "collect_vehicle_and_issue"
        }

    if any(word in msg for word in ["brakes", "oil change", "check engine", "tire", "alignment", "battery"]):
        return {
            "response": (
                "Got it. I can help get that scheduled. "
                "Please provide your vehicle year, make, model, and the best phone number to reach you."
            ),
            "next_step": "collect_contact_info"
        }

    return {
        "response": (
            f"Thanks, {greeting_name}. I’m here to help with scheduling, vehicle concerns, and service questions. "
            "Can you tell me what’s going on with your vehicle today?"
        ),
        "next_step": "collect_issue"
    }
    from fastapi import APIRouter
from app.models.schemas import CustomerMessage, AIResponse
from app.services.conversation import generate_receptionist_response

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/message", response_model=AIResponse)
def handle_message(payload: CustomerMessage):
    result = generate_receptionist_response(
        message=payload.message,
        customer_name=payload.customer_name
    )

    return AIResponse(
        response=result["response"],
        next_step=result["next_step"]
    )
    


@app.get("/health")
def health_check():
    return {"status": "ok"}
