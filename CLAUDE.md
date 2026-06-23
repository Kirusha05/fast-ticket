# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A ticketing app: FastAPI backend (Python 3.12, `uv`) + React/Vite frontend (TypeScript), backed by PostgreSQL 15 (run via `docker-compose.yaml`). Auth handled by Auth0 — the frontend gets a JWT, the backend validates it against Auth0's JWKS and lazily creates a `users` row on first authenticated request.

## Common commands

Backend (run from `backend/`):

```bash
docker compose up -d db          # start Postgres on :5432
uv run alembic upgrade head      # apply migrations
uv run uvicorn main:app --host 0.0.0.0 --port 8000          # dev server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level error  # prod-ish
uv run alembic revision -m "describe change"      # create empty migration (hand-written)
```

Frontend (run from `frontend/`):

```bash
npm run dev        # vite dev server
npm run build      # tsc -b && vite build
npm run lint       # eslint .
npm run preview    # preview built bundle
```

No test suite exists yet in either app — there are no `pytest`/`vitest` configs or test files.

## Backend architecture

Strict layered DDD-ish structure, all async. A request flows **routes → usecases → repositories → psycopg cursors**, with Pydantic `BaseEntity` models in between. There is no ORM — repositories write raw SQL.

- `main.py` — FastAPI app. DB connection pool is opened/closed in the `lifespan` context. Routers are mounted under prefixes (`/users`, …). CORS allows `*` with credentials off (do not combine `allow_credentials=True` with `*`).
- `config/config.py` — env loading. `MODE` env var (`local|test|dev|prod|cloud`) selects which `.env*` file Pydantic reads; `cloud` reads straight from env vars. Configs are nested (`config.DB`, `config.AUTH0`) and each uses a prefixed env namespace (`DB_`, `AUTH0_`).
- `config/db_session.py` — global `DB_POOL` (`psycopg.AsyncConnectionPool`). `get_db_session()` is the FastAPI dependency: yields a connection with `dict_row` row factory and **auto-commits on success / rolls back on exception**. Use this dependency to get a `conn`.
- `routes/deps/auth.py` — `get_current_user` validates the `Bearer` JWT (RS256, JWKS cached in-process) and returns a `User` entity, **creating one if the `auth0_id` is new** (uses `email`/`name` claims namespaced by `AUTH0_AUDIENCE`). This is the auth dependency; pair it with `get_db_session`.
- `models/` — Pydantic entities. `base.py` defines `EntityId` (a prefixed UUID, e.g. `u-<uuid>`, serialized as a string) and `BaseEntity` (has `id: EntityId` and a `ClassVar entity_id_prefix`). Each model declares its prefix (`u`, `e`, `s`, `b`).
- `repositories/` — `BaseRepository` ABC with `_map_db_model_to_entity`, plus CRUD. Repositories take an `AsyncConnection` and use `cursor()` directly. DB columns are raw UUIDs; entities are built via `Model.build_entity_id_from_uuid(data['id'])`.
- `usecases/` — orchestration. `BookingsUseCase` is the interesting one: it branches on `EventType` (`SEATED` locks seats via `get_seats_by_ids_for_update` + atomic `mark_seats_as_unavailable`; `OPEN_FIELD` uses atomic `decrement_available_tickets`). Cancellation reverses both.
- `migrations/` — Alembic. `env.py` pulls the connection string from `config.DB`. `**target_metadata = None`**, so `alembic revision --autogenerate` does not work — migrations are hand-written. Schema so far: `users`, `events`, `seats`, `bookings`, `booking_seats`.

Wiring status: `routes/users.py` is the only router registered in `main.py`. `EventsUseCase` and `BookingsUseCase` exist but have **no routes yet** — when adding them, follow the `users.py` pattern (`Depends(get_db_session)` + `Depends(get_current_user)` for the current user's `user.id`).

### ID conventions

Primary keys are time-ordered UUIDs (see `EntityId.generate_uuid` — uuid1 time bits grafted onto a uuid4 for index locality), stored as `UUID` columns but surfaced in the API as prefixed strings (`u-…`, `e-…`, `s-…`, `b-…`). Parse request strings with `EntityId.from_string(...)`; never pass a raw string where an `EntityId` is expected.

## Frontend architecture

Vite + React 19 + react-router 8. Auth0 is configured in `src/main.tsx` via `Auth0Provider` (domain/clientId hardcoded — `krrr.eu.auth0.com`, audience `https://fast-ticket.com`, `cacheLocation="localstorage"`). `src/App.tsx` is a demo: `getAccessTokenSilently()` then `fetch('http://localhost:8000/users/profile', { Authorization: Bearer ... })`. Backend calls should follow this pattern — attach the Auth0 access token as a Bearer header.

## Auth0 / env setup

`.env` (in `backend/`) holds `DB_`* and `AUTH0_*` values. The same Auth0 tenant/domain/clientId must match between `backend/.env` and `frontend/src/main.tsx`. The backend expects custom claims namespaced by `AUTH0_AUDIENCE` (e.g. `https://fast-ticket.com/email`) — ensure the Auth0 API is configured to emit those claims.