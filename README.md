# ApexAcquisitions

Real estate wholesaling and investment platform. Search distressed properties, manage your deal pipeline, match deals to cash buyers, and close faster.

## Features

- **Property Search** - Find pre-foreclosures, tax liens, probate, vacant, and absentee-owner properties
- **Deal Pipeline** - Track deals from lead to close with contracts and assignment fees
- **Investor Matching** - Match deals to buyer buy boxes by location, price, strategy
- **Contract Generation** - State-specific purchase agreements and assignment contracts
- **Skip Tracing** - Find owner contact info from verified data sources
- **User Auth** - Register, login, JWT-protected dashboard and settings

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000`

## Project Structure

```
app/
  main.py                  # FastAPI entry point
  models/
    database.py            # SQLAlchemy engine & session
    user.py                # User & UserSettings models
  schemas/
    user.py                # Pydantic request/response schemas
  routes/
    auth.py                # /api/auth (register, login, profile, settings)
    conversation.py        # /api/conversation (lead intake)
    pages.py               # HTML page routes
  services/
    auth.py                # Password hashing & JWT tokens
    conversation.py        # Lead qualification flow
templates/                 # Jinja2 HTML templates
static/                    # CSS & JS assets
migrations/                # PostgreSQL SQL migrations
```

## Environment Variables

```
APP_NAME=ApexAcquisitions
DATABASE_URL=postgresql://user:password@localhost:5432/apex_acquisitions
SECRET_KEY=change-me-to-a-random-secret-key
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Get profile |
| PATCH | `/api/auth/me` | Update profile |
| GET | `/api/auth/me/settings` | Get settings |
| PATCH | `/api/auth/me/settings` | Update settings |
| GET | `/api/health` | Health check |
