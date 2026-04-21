# AEGIS Prompt Firewall

Phase 1 of the AEGIS Autonomous Execution Guard for Intelligent Systems backend scanner.

This is a production-oriented, Python-first LLM firewall built with FastAPI, PostgreSQL, YARA, and LLM Guard.

## Architecture

* **FastAPI:** High-performance async API.
* **Scanners:** Extensible scanner abstraction (Regex, YARA, Unicode, LLM Guard).
* **Policy Engine:** Deterministic routing (ALLOW, SANITIZE, CHALLENGE, BLOCK).
* **Persistence:** PostgreSQL via asyncpg and SQLAlchemy async.
* **Validation:** Strict payload and size limits via Pydantic.

## Getting Started (Docker Compose)

The easiest way to run the firewall is via Docker Compose, which spins up the API and the PostgreSQL database.

```bash
cd prompt-firewall
docker compose up --build
```

### Endpoints

* `GET /health` : Liveness probe.
* `GET /ready` : Deep readiness check of DB and scanners.
* `POST /v1/scan` : Main prompt-scanning endpoint.
* `POST /api/analyze` : Temporary compatibility mapping for the legacy React dashboard.

## Manual Setup (Local Dev)

1. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Database**
   Export `DATABASE_URL` or modify `.env` to point to a working PostgreSQL instance.
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/aegis_db"
   ```

3. **Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Run Dev Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

Settings are loaded via environment variables or a `.env` file. You can adjust limits, disable LLM Guard for fast local testing, or change the DB URI.

```env
ENABLE_LLM_GUARD=false
LLM_GUARD_READINESS_MODE=degraded
MAX_PROMPT_CHARS=15000
```

## Testing

Note: Integration tests will connect to the active `DATABASE_URL` so spin up the database via docker-compose before running them locally.

```bash
pytest tests/unit/
pytest tests/integration/
```
