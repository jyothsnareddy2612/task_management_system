# Frontend Microservice

Standalone React 19 + TypeScript frontend microservice for the task management portal.

This service is intentionally outside the backend `src/` package:

```text
task_management_portal/
├── src/          # Python backend services
└── frontend/     # React frontend microservice
```

The folder structure follows the COE React Architecture guide:

- `src/app`: app shell and route constants
- `src/config`: environment and static app constants
- `src/components`: shared generic UI only
- `src/features`: domain code grouped by feature
- `src/hooks`: shared hooks
- `src/layouts`: page-level layouts
- `src/lib`: third-party client wrappers and storage helpers
- `src/services`: cross-feature API/error helpers
- `src/styles`: global styles
- `src/types`: global TypeScript contracts
- `src/utils`: pure helper functions

Run locally:

```powershell
cd frontend
npm install
npm run dev
```

The app runs on:

```text
http://localhost:5173
```

Environment variables:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_AUTH_BASE_URL=http://localhost:8001/api/v1
```
