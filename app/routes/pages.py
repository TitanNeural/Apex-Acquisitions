"""
Page routes - serves the frontend HTML templates.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/properties", response_class=HTMLResponse)
def properties_page(request: Request):
    return templates.TemplateResponse(request, "properties.html")


@router.get("/deals", response_class=HTMLResponse)
def deals_page(request: Request):
    return templates.TemplateResponse(request, "deals.html")
