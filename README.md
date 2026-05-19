# Task Management System

Production-grade async backend scaffold for task assignment, worker progress tracking, comments, realtime updates, audit history, observability, and resiliency patterns.

## Run Locally Without Docker

```powershell
uv venv
uv pip install -r requirements/dev.txt
Copy-Item .env.example .env
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
uv run uvicorn auth.app:app --reload --port 8001
uv run streamlit run src/frontend/streamlit_app.py
```

## Google OAuth Login

The app supports both normal email/password login and Google OAuth login.

In Google Cloud Console, create an OAuth Client ID for a Web application and add this authorized redirect URI:

```text
http://localhost:8001/api/v1/auth/google/callback
```

Then set these values in `.env`:

```text
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8001/api/v1/auth/google/callback
OAUTH_SUCCESS_REDIRECT_URL=http://localhost:5173
GOOGLE_ADMIN_EMAILS=["admin@example.com"]
```

Admin assignment is controlled by `GOOGLE_ADMIN_EMAILS`. Users whose verified Google email is in that list become `ADMIN`; everyone else becomes `WORKER`. Do not ask users to choose their own role after login, because that lets anyone self-promote.

Start login by opening:

```text
http://localhost:8001/api/v1/auth/google/login
```

After Google redirects back, the backend creates or finds a local `WORKER` user by verified email and returns the same JWT `access_token` and `refresh_token` used by protected APIs.

## Architecture Notes

Routes are thin HTTP adapters. Services own business rules and transactions. Repositories own persistence queries. Middleware supplies request IDs, access logs, metrics, and centralized error mapping. Redis pub/sub decouples task changes from WebSocket and SSE delivery.

SSE is included for one-way, browser-friendly event streaming such as admin dashboards and task feeds. WebSockets are included for bidirectional realtime workflows where workers or dashboards may later send live commands, acknowledgements, or presence signals. At scale, both need shared fanout through Redis, sticky-session awareness, auth on connection setup, backpressure handling, and per-tenant channel isolation.

Retries and timeouts belong at integration boundaries, not inside database transactions. The `BaseHttpClient` uses `httpx` plus `tenacity` for transient network failures. Production systems should add idempotency keys to retry-safe writes, circuit breaker state, dead-letter handling, and dashboards for retry exhaustion.

Security defaults include JWT access/refresh tokens, bcrypt hashing, OAuth2 bearer extraction, RBAC, typed request validation, protected routes, and no business logic in route functions. Production hardening should rotate secrets, store refresh-token families, add revocation, enforce HTTPS, rate-limit auth endpoints, and audit privileged actions.

Observability includes structured JSON logs, request correlation IDs, latency/status logging, Prometheus metrics, and tracing placeholders. Logs should carry `request_id`, `user_id`, endpoint, latency, and status code so failures can be followed across API, workers, Redis, and downstream integrations.

## Day Plan

Day 1 covers project setup, uv, Ruff, MyPy, folder structure, PostgreSQL, SQLAlchemy, Alembic, DB schema, and health endpoints.
Day 2 adds JWT auth, RBAC, login/register, refresh tokens, and auth middleware.
Day 3 adds task CRUD, comments, repositories, services, pagination, and filtering.
Day 4 adds WebSockets, SSE, Redis, and realtime task events.
Day 5 adds structured logging, metrics, tracing boundaries, retries, timeout handling, and resiliency documentation.
Day 6 expands pytest unit, integration, and e2e coverage, including rollback, permissions, WebSocket, and SSE cases.
Day 7 focuses on rate limiting, security hardening, deployment readiness, CI/CD, and production review.
