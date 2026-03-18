"""
EAS Tire & Auto - AI Receptionist (Makayla)
FastAPI application entry point
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routes.voice import router as voice_router
from app.routes.api import router as api_router

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# App lifecycle
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"🚗 {settings.business_name} AI Receptionist '{settings.receptionist_name}' starting up …"
    )
    yield
    logger.info("Shutting down.")


# ──────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        f"AI Receptionist '{settings.receptionist_name}' for {settings.business_name}. "
        "Handles inbound calls via Twilio, powered by Claude AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Static files (CSS / JS)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routers
app.include_router(voice_router)
app.include_router(api_router)


# ──────────────────────────────────────────────
# Root / health
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "receptionist": settings.receptionist_name,
        "business": settings.business_name,
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
