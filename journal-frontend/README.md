# Journaling Companion — Frontend

React + Vite + TypeScript + Tailwind + shadcn/ui. Connects to FastAPI backend with routes for auth/users/entries/insights.

## Quick start
```bash
npm install
npm run dev
```
By default it expects the backend at `http://localhost:8000` with the following bases:
- AUTH: `/auth`
- USERS: `/users`
- ENTRIES: `/entries`
- INSIGHTS: `/insights`

You can override via a `.env` file:
```
VITE_API_BASE=http://localhost:8000
VITE_AUTH_BASE=/auth
VITE_USERS_BASE=/users
VITE_ENTRIES_BASE=/entries
VITE_INSIGHTS_BASE=/insights
```

## Notes
- JWT is stored in `localStorage` under `token`.
- Analytics pulls insights per entry; if an entry has no insight yet, it is skipped.
- The "AI Coach" modules are placeholders ready to be wired to your model endpoints.
