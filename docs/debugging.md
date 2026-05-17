# Debugging Guide

## FastAPI

Run normally:

```powershell
uv run uvicorn src.main:app --reload
```

Use VS Code configuration `FastAPI: uvicorn` to set breakpoints in routes, services, repositories, and middleware.

Important places to debug:

- `src/api/rest/routes/*`: HTTP request parsing and dependency wiring.
- `src/core/services/*`: business rules and permissions.
- `src/data/repositories/*`: SQL query behavior.
- `src/api/middleware/error_handler.py`: unexpected exceptions.

## Streamlit

Run normally:

```powershell
uv run streamlit run src/frontend/streamlit_app.py
```

Use VS Code configuration `Streamlit` to debug UI orchestration and API calls.

## Common Failures

### `relation "users" does not exist`

Run migrations against the same `DATABASE_URL` used by the backend:

```powershell
uv run alembic upgrade head
```

### Google callback returns 500

Check backend logs. If Google token/profile calls are `200 OK`, the failure is usually local DB, user creation, or JWT issuing.

### Streamlit says `No module named src`

Run Streamlit from the repository root:

```powershell
uv run streamlit run src/frontend/streamlit_app.py
```

### Task create times out

If Redis is not running, realtime publishing should degrade after one second. Check backend logs for `Realtime publish skipped`.

## Test Debugging

Run all tests:

```powershell
uv run pytest
```

Debug tests with the VS Code `Pytest` launch config.

