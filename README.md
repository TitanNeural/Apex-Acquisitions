# 🚗 EAS Tire & Auto — AI Receptionist (Makayla)

Makayla is a fully automated AI phone receptionist for **EAS Tire & Auto**.
She answers inbound calls, collects customer info, understands service needs, and books appointments — all hands-free.

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Voice** | Amazon Polly "Joanna" (natural female voice via Twilio) |
| **AI Brain** | Anthropic Claude (claude-haiku-4-5) |
| **Phone** | Twilio – inbound call handling + speech-to-text |
| **Conversation** | Multi-turn, context-aware |
| **Data capture** | Name · Phone · Vehicle · Service need · Appointment |
| **Human handoff** | Transfers upset/complex callers to a live tech |
| **Web chat** | Text-based test interface (no phone needed) |
| **Dashboard** | Live admin dashboard at `/api/dashboard` |
| **API** | REST API + auto-generated docs at `/docs` |

---

## 🗂️ Project Structure

```
AI-Receptionist/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings (loaded from .env)
│   ├── routes/
│   │   ├── voice.py             # Twilio webhook handlers
│   │   └── api.py               # REST API + dashboard
│   ├── services/
│   │   ├── conversation.py      # Conversation session manager
│   │   ├── ai_service.py        # Claude AI integration
│   │   └── voice_service.py     # TwiML / voice response builder
│   ├── models/
│   │   └── schemas.py           # Pydantic schemas
│   └── templates/
│       └── index.html           # Admin dashboard UI
├── static/                      # CSS / JS assets
├── run.py                       # Dev launcher
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd AI-Receptionist
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your keys:
#   ANTHROPIC_API_KEY  – from console.anthropic.com
#   TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_PHONE_NUMBER
#   BASE_URL           – public URL Twilio can reach (see step 4)
```

### 3. Run the server

```bash
python run.py
# or
uvicorn app.main:app --reload
```

Open http://localhost:8000/api/dashboard to see the dashboard.
Open http://localhost:8000/docs for the interactive API docs.

### 4. Expose locally with ngrok (for Twilio testing)

```bash
ngrok http 8000
# Copy the https URL and set BASE_URL=https://xxxx.ngrok.io in .env
```

### 5. Configure Twilio

In the [Twilio Console](https://console.twilio.com):

1. Go to **Phone Numbers → Manage → Active numbers** → click your number
2. Under **Voice Configuration → A call comes in**, set:
   - Webhook: `https://your-ngrok-url/voice/incoming`
   - Method: `HTTP POST`
3. Under **Call Status Changes**, set:
   - Webhook: `https://your-ngrok-url/voice/status`
4. Save.

Now call your Twilio number — Makayla will answer! 🎉

---

## 🧪 Test Without a Phone

Use the built-in web chat at `http://localhost:8000/api/dashboard` or call the API directly:

```bash
# Start a new session
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{}'

# Continue the session (use the call_sid returned above)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"call_sid": "web_anon", "message": "Hi, I need an oil change"}'
```

---

## 🔁 Call Flow

```
Customer calls Twilio number
        │
        ▼
POST /voice/incoming
  • New Conversation session created
  • Makayla greets caller (Polly.Joanna voice)
        │
        ▼  (caller speaks)
POST /voice/gather  (Twilio sends SpeechResult)
  • Claude AI generates Makayla's reply
  • Customer data extracted (name, vehicle, etc.)
  • Next action decided: listen | end_call | transfer
        │
   ┌────┴────────────────┐
   │                     │
listen              end_call / transfer
   │                     │
   ▼                     ▼
 Loop             Hang up / Dial tech
```

---

## 🌐 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| GET | `/api/dashboard` | Admin dashboard (HTML) |
| GET | `/api/conversations` | List all call sessions |
| GET | `/api/conversations/{call_sid}` | Session detail + history |
| POST | `/api/chat` | Text chat with Makayla |
| POST | `/voice/incoming` | Twilio: new inbound call |
| POST | `/voice/gather` | Twilio: speech transcription |
| POST | `/voice/no-input` | Twilio: silence fallback |
| POST | `/voice/status` | Twilio: call status callback |

---

## 🛠️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude AI API key |
| `TWILIO_ACCOUNT_SID` | ✅ (voice) | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | ✅ (voice) | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | ✅ (voice) | Your Twilio phone number |
| `BASE_URL` | ✅ (voice) | Public URL for Twilio webhooks |
| `BUSINESS_NAME` | optional | Defaults to "EAS Tire & Auto" |
| `RECEPTIONIST_NAME` | optional | Defaults to "Makayla" |
| `BUSINESS_HOURS` | optional | Spoken by Makayla when asked |
| `BUSINESS_ADDRESS` | optional | Spoken by Makayla when asked |
| `BUSINESS_PHONE` | optional | Used for human transfer fallback |

---

## 🏗️ Tech Stack

- **FastAPI** – async web framework
- **Twilio** – phone call handling + speech-to-text
- **Anthropic Claude** – AI brain (claude-haiku-4-5 for speed)
- **Amazon Polly (Joanna)** – natural female voice (via Twilio)
- **Uvicorn** – ASGI server
- **Jinja2** – dashboard templating
