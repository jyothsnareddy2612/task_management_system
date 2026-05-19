# Auth Microservice

This service isolates register, login, refresh, Google OAuth, and `/me` into a standalone FastAPI app.

Run locally:

```powershell
Copy-Item auth/.env.example auth/.env
uvicorn auth.app:app --reload --port 8001
```

Routes:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/google/login`
- `GET /api/v1/auth/google/callback`
- `GET /api/v1/auth/me`

The microservice currently reuses the existing database models, repositories, auth service, JWT helpers, settings, and error middleware. That keeps the first split small while making it possible to deploy auth separately from the task API.
