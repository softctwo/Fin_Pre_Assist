# Repository Guidelines

## Project Structure & Module Organization
The repo is split between `backend/` (FastAPI) and `frontend/` (React + Vite). Within `backend/app`, `api/` exposes routes, `core/` stores config, `models/` define SQLAlchemy tables, and `services/` implement document, template, and vector logic; migrations sit under `alembic/`, uploads in `storage/`, and tests in `backend/tests` plus `test_cache_*.py`. The client lives in `frontend/src` with `components/`, `pages/`, `services/`, and Zustand `store/`, while `docker-compose.yml` wires the stack for local orchestration.

## Build, Test & Development Commands
`docker-compose up -d` launches Postgres, API, UI, and monitoring. For backend-only work run `cd backend && python app/main.py`, apply migrations via `alembic upgrade head`, and execute `bash run_tests.sh` for the full suite plus coverage. Frontend development relies on `cd frontend && npm run dev`; ship-ready bundles use `npm run build`, and `npm run lint` keeps ESLint happy. Use `pytest tests/ -k feature -v --cov=app` when iterating on a specific module.

## Coding Style & Naming Conventions
Format Python with Black (88 columns) and sorted imports via isort; validate with `flake8 app/ --max-line-length 120` plus `mypy app/`. Name services with verb-first modules (`services/document_processor.py`), keep models in PascalCase, and surface DTOs through Pydantic schemas. The frontend follows TypeScript strict mode, two-space indents, PascalCase component files, camelCase hooks, and colocated styling. Run `npm run lint` and `black app/ tests/` before committing.

## Testing Guidelines
Pytest drives unit, integration, and E2E coverage. Place specs under `backend/tests` as `test_<feature>.py`, prefer async HTTPX clients for API coverage, and maintain ≥80 % line coverage (view `test_reports/coverage/index.html`). Use `bash run_tests.sh` to regenerate HTML reports. UI-affecting changes should include a short manual checklist or Playwright/Cypress script referencing the impacted route.

## Commit & Pull Request Guidelines
History follows Conventional Commits (`docs:`, `test:`, `feat(api): ...`). Keep subjects under 72 characters, describe scope in the body, and note breaking changes explicitly. Each PR must state motivation, linked issues, env/migration impacts, and verification steps (`pytest`, `npm run lint`, screenshots for UI`) before requesting review.

## Security & Configuration Tips
Copy `.env.example` to `.env` files and inject secrets (`AI_PROVIDER`, `OPENAI_API_KEY`, DB creds) via overrides or secret managers—never commit them. Validate uploads through `services/document_processor.py`, run `bandit app/` + `safety check` on security-sensitive changes, and keep `grafana/` + `prometheus/` configs aligned with exported metrics.
