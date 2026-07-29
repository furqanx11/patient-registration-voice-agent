# Voice AI Agent — Patient Registration

A dialable phone number + REST API that conversationally registers U.S. patients and persists their demographic data. Built with FastAPI, SQLAlchemy, SQLite, and Vapi.

## Live Demo

- **Phone number:** [FILL IN after Vapi provisioning]
- **API base URL:** [FILL IN after deployment, e.g. https://your-app.up.railway.app]
- **Repo:** [FILL IN your GitHub URL]

## Architecture

```
Caller ↔ Vapi (telephony + STT/TTS + GPT-4o orchestration)
              ↕ (function calls + webhooks, HTTPS/JSON)
         FastAPI backend ↔ SQLite (patients.db)
              ↕
         REST API (same service, for external querying)
```

- **Telephony + Voice AI:** Vapi. It abstracts telephony, STT, and TTS so the focus stays on conversation design, backend correctness, and error handling — the right trade-off under a 3-hour constraint.
- **LLM:** GPT-4o via Vapi's model integration, chosen for strong conversational quality and reliable function calling.
- **Backend:** Python + FastAPI (async), with Pydantic for server-side validation.
- **Database:** SQLite (file-backed, survives restarts). SQLAlchemy is used so migrating to Postgres later only requires changing `DATABASE_URL`.
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

2. **Run the server:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   On first run, `patients.db` is created and seeded with one demo patient (Jane Doe).

3. **Expose it:**
   - Quick local test: `ngrok http 8000` and use the ngrok HTTPS URL.
   - Production: deploy the Docker image (see below).

4. **Configure Vapi:**
   - Create an account and provision a phone number.
   - Import `vapi_assistant_config.json` (or paste the system prompt and recreate the three tools).
   - Replace every `https://YOUR_BACKEND_URL` placeholder with your deployed/ngrok URL.
   - Set `serverUrl` to `https://YOUR_BACKEND_URL/calls/webhook/vapi` so Vapi can post call transcripts.
   - Set `serverUrlSecret` to a random string and configure it in Vapi if you want webhook verification (verification not implemented in this base version; see Next Steps).
   - Add your OpenAI and ElevenLabs API keys in Vapi's dashboard.

5. **Call the number** and register a patient. Call again with the same phone number to confirm duplicate detection and persistence.

## Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string. Defaults to `sqlite:///./patients.db`. | No |
| `BACKEND_URL` | Used only for rendering README/Vapi placeholders. | No |
| `LOG_LEVEL` | Logging level. Default `INFO`. | No |
| `ENVIRONMENT` | `development` or `production`. Enables SQLAlchemy echo in dev. | No |

No LLM/telephony API keys live in this repo — those are configured in the Vapi dashboard.

## API Reference

All responses use the envelope `{ "data": ..., "error": ... }`.

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

### Option 1: Railway (recommended for simplicity)

Railway has a free tier and supports persistent disks. Steps:
1. Push this repo to GitHub.
2. Create a Railway project from the GitHub repo.
3. Add a **persistent volume** mounted at `/app` so `patients.db` survives deploys.
4. Set the start command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`.
5. Railway gives you a public HTTPS URL; paste it into Vapi.

### Option 2: Render

Render also has persistent disks on paid plans. Use the included Dockerfile as the build/run source and add a disk mount at `/app`.

### Option 3: Fly.io

Fly.io has volumes:
```bash
fly launch
fly volumes create patient_data --size 1 --region iad
fly deploy
```
Mount the volume at `/app` in `fly.toml` so the SQLite file persists.

### Option 4: Docker (anywhere)

```bash
docker build -t patient-registration .
docker run -p 8000:8000 -v $(pwd)/data:/app/data patient-registration
```

Use a volume (`-v`) so the SQLite file is not lost when the container restarts. For production with real traffic, the best next step is to swap SQLite for a managed Postgres (Neon, Supabase, Railway Postgres, etc.) by changing `DATABASE_URL`.

### Recommendation

For this assessment, **Railway + a persistent disk** is the fastest path to a live, callable number. If you want zero persistence concerns, use **Railway Postgres** instead of SQLite.

## Known Limitations / Trade-offs

- **SQLite** instead of Postgres — fine for assessment scale; use a persistent disk or switch to Postgres for real traffic.
- **No authentication** on the API — acceptable for a technical assessment holding no real patient data, not acceptable for production.
- **Webhook verification** is not implemented. Vapi signs webhooks with `serverUrlSecret`, but this version does not verify the signature. Add HMAC verification before accepting production traffic.
- **Voice-side robustness** (interruptions, heavy accents, multi-language) depends on Vapi/GPT-4o's built-in handling; not independently hardened beyond the system prompt.
- **Appointment scheduling, multi-language switching, and a web dashboard** were treated as bonus/stretch and are not implemented in the base submission.
- **Basic input sanitization** is handled through Pydantic validation; no additional rate-limiting or abuse protection has been added.

## Next Steps (if given more time)

- Add HMAC verification for Vapi webhooks.
- Add a minimal read-only dashboard (simple HTML table view) over `GET /patients`.
- Add more granular observability (structured JSON logs, request IDs).
- Add automated integration tests for the full voice flow using mocked Vapi payloads.
- Migrate to Postgres with Alembic migrations for schema versioning.
