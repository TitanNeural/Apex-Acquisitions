"""
FastAPI application entry point for ApexAcquisitions.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.models.database import init_db
from app.routes import auth, conversation, pages

# Create tables on import (idempotent - safe to call multiple times)
init_db()


app = FastAPI(
    title=os.getenv("APP_NAME", "ApexAcquisitions"),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["Conversation"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": os.getenv("APP_NAME", "ApexAcquisitions")}
