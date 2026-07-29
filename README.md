# Voice AI Agent — Patient Registration

A dialable phone number + REST API that conversationally registers U.S. patients and persists their demographic data. Built with FastAPI, SQLAlchemy, PostgreSQL, and Vapi.

## Live Demo

- **Phone number:** +1 (207) 559-2161
- **API base URL:** https://patient-registration-voice-agent-1.onrender.com
- **Repo:** https://github.com/furqanx11/patient-registration-voice-agent

## Architecture

```
Caller ↔ Vapi (telephony + STT/TTS + GPT-4o orchestration)
              ↕ (function calls + webhooks, HTTPS/JSON)
         FastAPI backend ↔ PostgreSQL (Render Postgres)
              ↕
         REST API (same service, for external querying)
```

- **Telephony + Voice AI:** Vapi. It abstracts telephony, STT, and TTS so the focus stays on conversation design, backend correctness, and error handling.
- **LLM:** GPT-4o via Vapi's model integration, chosen for strong conversational quality and reliable function calling.
- **Backend:** Python + FastAPI (async), with Pydantic for server-side validation.
- **Database:** PostgreSQL via Render Postgres. SQLAlchemy is used as the ORM, so the database layer is portable.
- **Call logging:** Every call webhook from Vapi is stored in `call_logs` and linked to an existing patient by phone number when possible.

## Project Structure

```
.
├── src/
│   ├── api/v1/routes/          # FastAPI routers mounted at root (patients, calls, Vapi tools)
│   ├── controllers/            # HTTP-layer logic / request orchestration
│   ├── services/               # Business logic
│   ├── repositories/           # Database access layer
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic request/response models
│   ├── utils/                  # Helpers (logging, phone normalization, seed, response envelope)
│   ├── config.py               # Pydantic settings (.env aware)
│   ├── database.py             # Engine + session + Base
│   └── main.py                 # App factory and exception handlers
├── tests/                      # pytest + FastAPI TestClient
├── vapi_assistant_config.json  # Vapi assistant configuration (prompt + tools + webhook)
├── Dockerfile
├── requirements.txt
└── .env.example
```

The design follows OOP and DRY:
- A generic `BaseRepository` removes repeated CRUD code.
- `envelope()` is the single response-format helper.
- `normalize_phone()` is reused in schemas, services, and repositories.
- All services, controllers, and repositories are class-based and injected with a `Session`.

## Setup Instructions

1. **Clone and install:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Run the server locally:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Local development defaults to SQLite (`patients.db`).

3. **Expose it for local testing:**
   - Quick local test: `ngrok http 8000` and use the ngrok HTTPS URL.
   - Update the `BACKEND_URL` in your `.env` to the ngrok URL.

4. **Configure Vapi:**
   - Create an account and provision a phone number.
   - Import `vapi_assistant_config.json` (or paste the system prompt and recreate the three tools).
   - Replace every `https://YOUR_BACKEND_URL` placeholder with your deployed/ngrok URL.
   - Set `serverUrl` to `https://YOUR_BACKEND_URL/calls/webhook/vapi` so Vapi can post call transcripts.

5. **Call the number** and register a patient. Call again with the same phone number to confirm duplicate detection and persistence.

## Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string. Use `postgresql://...` for production (Render Postgres) or `sqlite:///./patients.db` for local dev. | No |
| `BACKEND_URL` | Used for rendering README/Vapi placeholders. | No |
| `LOG_LEVEL` | Logging level. Default `INFO`. | No |
| `ENVIRONMENT` | `development` or `production`. Enables SQLAlchemy echo in dev. | No |

No LLM/telephony API keys live in this repo — those are configured in the Vapi dashboard.

## API Reference

All responses use the envelope `{ "data": ..., "error": ... }`.

Base URL: `https://patient-registration-voice-agent-1.onrender.com`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/patients` | List patients. Optional `?last_name=`, `?date_of_birth=`, `?phone_number=` |
| GET | `/patients/{id}` | Get one patient by UUID |
| POST | `/patients` | Create patient (201 on success, 422 on validation failure) |
| PUT | `/patients/{id}` | Partial update |
| DELETE | `/patients/{id}` | Soft-delete (sets `deleted_at`) |
| GET | `/patients/lookup/by-phone/{phone}` | Duplicate-detection lookup (REST-friendly) |
| POST | `/calls/webhook/vapi` | Vapi end-of-call webhook (stores transcript + links to patient) |
| GET | `/calls/patient/{patient_id}` | Call transcripts for a patient |
| POST | `/tools/lookup-by-phone` | Vapi tool adapter for phone lookup |
| POST | `/tools/update-patient` | Vapi tool adapter for patient update |

## Running Tests

```bash
pytest
```

Tests cover patient CRUD, validation, duplicate detection, soft deletes, and Vapi webhook handling with an in-memory SQLite database.

## Deployment

### Deployed on Render

This app is deployed on Render using:

- **Render Web Service** running the Docker image from the included `Dockerfile`.
- **Render Postgres** for the database.
- Environment variables set in the Render dashboard:
  - `DATABASE_URL` → Internal Database URL from Render Postgres
  - `ENVIRONMENT` → `production`

### Render Deployment Steps (for reference)

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** and connect the GitHub repo.
3. Select **Docker** as the runtime.
4. Set the environment variables above.
5. Create a **Render Postgres** database and copy its **Internal Database URL** into `DATABASE_URL`.
6. Render gives you a public HTTPS URL; paste it into Vapi.

### Docker (anywhere)

```bash
docker build -t patient-registration .
docker run -d -p 8000:8000 -e ENVIRONMENT=production patient-registration
```

For local Docker with SQLite persistence:

```bash
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data -e DATABASE_URL=sqlite:///./data/patients.db patient-registration
```

## Known Limitations / Trade-offs

- **No authentication** on the API — acceptable for a technical assessment holding no real patient data, not acceptable for production.
- **Voice-side robustness** (interruptions, heavy accents, multi-language) depends on Vapi/GPT-4o's built-in handling; not independently hardened beyond the system prompt.
- **Appointment scheduling, multi-language switching, and a web dashboard** were treated as bonus/stretch and are not implemented in the base submission.
- **Basic input sanitization** is handled through Pydantic validation; no additional rate-limiting or abuse protection has been added.

## Next Steps (if given more time)

- Add HMAC verification for Vapi webhooks.
- Add a minimal read-only dashboard (simple HTML table view) over `GET /patients`.
- Add more granular observability (structured JSON logs, request IDs).
- Add automated integration tests for the full voice flow using mocked Vapi payloads.
- Add Alembic migrations for schema versioning.
