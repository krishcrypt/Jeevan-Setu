# JeevanSetu AI – Backend (M2)

FastAPI backend for the **JeevanSetu AI – Public Health Chatbot** (SIH project).

This is the initial scaffold only: clean project structure, health checks,
and a mock `/chat` endpoint. No AI/RAG (M1), no WhatsApp/SMS (M3), no auth,
no database yet — but the structure is built so those slot in without a
rewrite.

## Project structure

```
jeevansetu-backend/
├── app/
│   ├── main.py                  # FastAPI app instance, CORS, router mounting
│   ├── core/
│   │   └── config.py             # Centralized settings (env vars)
│   ├── api/
│   │   └── v1/
│   │       ├── router.py         # Aggregates all v1 endpoint routers
│   │       └── endpoints/
│   │           ├── health.py     # /health, /ping, /info
│   │           └── chat.py       # /chat (mock reply for now)
│   ├── schemas/
│   │   └── chat.py               # Pydantic request/response models
│   ├── services/
│   │   ├── ai/
│   │   │   └── chatbot_service.py     # M1 plugs in here
│   │   └── messaging/
│   │       ├── whatsapp_service.py    # M3 plugs in here
│   │       └── sms_service.py         # M3 plugs in here
│   └── models/                   # Reserved for future DB models
├── requirements.txt
├── .env.example
└── .gitignore
```

**Where new things go later:**
- **M1 (AI/RAG):** implement `get_ai_response()` in `app/services/ai/chatbot_service.py`,
  then call it from `app/api/v1/endpoints/chat.py` instead of the mock reply.
- **M3 (WhatsApp/SMS):** implement `whatsapp_service.py` / `sms_service.py`,
  add `app/api/v1/endpoints/whatsapp.py` and `sms.py` webhook routers, and
  register them in `app/api/v1/router.py`.
- **Auth:** add `app/api/v1/endpoints/auth.py` + `app/core/security.py`, register in the router.
- **Database:** add models under `app/models/`, a `app/db/session.py`, and set `DATABASE_URL` in `.env`.

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
```

## Run the server

```bash
uvicorn app.main:app --reload
```

Server runs at: http://127.0.0.1:8000

## Test it

- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

Or via curl:

```bash
# Root
curl http://127.0.0.1:8000/

# Health check
curl http://127.0.0.1:8000/api/v1/health

# Service info
curl http://127.0.0.1:8000/api/v1/info

# Mock chat endpoint
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the symptoms of dengue?"}'
```

Expected chat response:

```json
{
  "reply": "Received your message: 'What are the symptoms of dengue?'. AI/RAG response generation is not implemented yet.",
  "session_id": null
}
```
