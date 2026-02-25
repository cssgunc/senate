# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack web application for the UNC Chapel Hill Undergraduate Senate (CS+SG project). Provides a public-facing site for students to navigate senate resources, search legislation, and look up senators by district, plus an admin dashboard for non-technical staff to manage content.

## Tech Stack

- **Backend**: Python 3.13, FastAPI 0.115, SQLAlchemy 2.0, SQL Server Express, pyodbc
- **Frontend**: Node.js 24 LTS, Next.js 15.5 (App Router), React 19, TypeScript 5.7, Tailwind CSS 3.4

## Development Environment

This project uses VS Code Dev Containers (Docker-based). The dev container runs Python 3.13-slim with Node.js 24 LTS, SQL Server Express 2022, and auto-installs all dependencies via `post_create.sh`.

Environment files must exist before building the container:
- `backend/.env` (copy from `backend/.env.example`)
- `frontend/.env.local` (copy from `frontend/.env.local.example`)

## Common Commands

### Running the App

```bash
# Backend (from /workspace/backend)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from /workspace/frontend)
npm run dev
```

The VS Code debugger has "Backend", "Purge & Frontend", and "Full Stack" launch configs.

### Testing

```bash
# Run all backend tests (from /workspace/backend)
pytest

# Run a single test file
pytest tests/test_main.py

# Run a specific test
pytest tests/test_main.py::test_health_check
```

### Linting

```bash
# Frontend (from /workspace/frontend)
npm run lint

# Backend uses Ruff (auto-formats on save in VS Code)
```

### Database

```bash
# From /workspace/backend:
python -m script.create_db          # Create dev database and tables
python -m script.create_test_db     # Create test database
python -m script.reset_dev          # Reset dev DB with mock data (interactive confirmation)
```

## Architecture

### Backend (`backend/`)

FastAPI app with entry point at `app/main.py`. Routers are registered via `app.include_router()`. Database sessions are injected via FastAPI's `Depends(get_db)` from `app/database.py`.

Key directories:
- `app/models/` — SQLAlchemy models (inherit from `app.database.Base`)
- `app/routers/` — API route modules
- `app/schemas/` — Pydantic request/response models
- `script/` — Database management scripts
- `tests/` — pytest tests using httpx `TestClient`

API docs available at `http://localhost:8000/docs` when running.

### Frontend (`frontend/`)

Next.js App Router with pages in `src/app/`. Uses `"use client"` directive for interactive components.

Key conventions:
- `src/lib/api.ts` — centralized `fetchAPI()` helper; all backend calls go through this
- `src/components/` — reusable React components
- Import alias: `@/` maps to `./src/`
- `NEXT_PUBLIC_API_URL` env var controls the backend URL (defaults to `http://localhost:8000`)

### PR Template

PRs follow the template in `.github/template-pr.md`: motivation, list of changes, and `Closes #XX` for issue linking.
