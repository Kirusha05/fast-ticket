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

Vite 8 + React 19 + TypeScript (strict), styled with Tailwind CSS 4 + ShadCN (`radix-nova` style, `neutral` base color, lucide icons). Routing is **TanStack Router** (file-based, *not* react-router despite the latter being in `package.json`); data fetching is **TanStack Query**; client state is **Zustand** (installed, not yet wired). Auth0 via `@auth0/auth0-react`. `@` aliases to `src/`.

> **All future frontend work must follow the structure below.** The layered feature-based layout and the `api → hooks → components` split are intentional — keep new code in the matching layer.

### App shell (`src/app/`)

- `main.tsx` — the real entry point (note: `src/main.tsx` was deleted; the old `src/App.tsx` demo is dead code). Renders `<Providers />` into `#root`.
- `providers.tsx` — the provider stack, outer→inner: `Auth0Provider` → `QueryClientProvider` → `RouterProvider`. Auth0 reads `VITE_AUTH0_DOMAIN` / `VITE_AUTH0_CLIENT_ID` / `VITE_AUTH0_AUDIENCE`, `cacheLocation="localstorage"`, `redirect_uri = window.location.origin`.
- `query-client.ts` — singleton `queryClient` (retry 0, staleTime 60s, refetchOnWindowFocus). Imported directly by hooks for `invalidateQueries`.
- `router.tsx` — `createRouter({ routeTree })`. Register the router type via `// See src/routeTree.gen.ts` (TanStack's `RouterProvider` generics are inferred from the generated tree).

### Routing (`src/routes/`)

File-based; **do not hand-edit `src/routeTree.gen.ts`** — the `@tanstack/router-plugin` (in `vite.config.ts`, `autoCodeSplitting: true`) regenerates it on dev/build from the files here. Add a route = add a file, e.g. `src/routes/events.tsx` → `/events`, `src/routes/events_.$eventId.tsx` → `/events/$eventId`. Each file does `export const Route = createFileRoute("/...")({ ... })`. The root layout lives in `__root.tsx` (currently a bare `<nav>` + `<Outlet>` + devtools — to be replaced by the sidebar/navbar shell).

### Features (`src/features/<feature>/`)

Each feature is self-contained and layered. **`features/events` is the reference implementation — mirror it for new features.**

- `types.ts` — TS types mirroring the backend Pydantic models (`Event`, `EventSeat`, `EventTier`, `CreateEventRequest`, etc.). Keep this in sync with `backend/models/`.
- `api/` — one file per endpoint. Pure async functions taking `(auth, body?)`, get the token via `auth.getAccessTokenSilently()`, then call `apiFetch`. Example: `create-event.ts`.
- `hooks/` — one file per endpoint wrapping the api fn in `useQuery`/`useMutation`. The hook owns the `useAuth0()` call so components stay dumb. Mutations invalidate the relevant query key (e.g. `["events"]`) on success. Example: `useCreateEvent.ts`.
- `stores/` — Zustand stores for feature-local client state (form/session state that doesn't come from the server). One store per concern, e.g. `useCreateEventStore.ts`. Components subscribe with narrow selectors (`useStore(s => s.field)`) to avoid broad re-renders — keep per-input/per-cell subscriptions, never select the whole store. Server-derived state stays in TanStack Query, not here.
- `components/` — feature UI, split by sub-entity (`components/events/`, `components/event/`). `index.ts` re-exports the public components + any Zod search schemas (e.g. `eventsSearchSchema`) consumed by routes. Routes import from this barrel, never from deep paths.

### Shared (`src/components/`, `src/lib/`, `src/hooks/`)

- `components/ui/` — ShadCN primitives (only `button.tsx` so far). Add more via the shadcn CLI; they land here. Keep them untouched/generated.
- `components/layout/` — app-level layout chrome (sidebar, navbar). `Sidebar.tsx` is currently a stub.
- `lib/utils.ts` — `cn()` (clsx + tailwind-merge) and **`apiFetch<T>(url, { authToken, ...init })`**, the single fetch wrapper. It prepends `VITE_API_BASE_URL`, sets `Content-Type: application/json`, attaches `Authorization: Bearer <token>` when `authToken` is passed, and returns parsed JSON. **All backend calls go through `apiFetch`** — never call `fetch` directly. Note the URL convention: pass a path like `/events` (the `apiFetch` docstring suggests a trailing slash; match whatever the mounted backend router expects).
- `hooks/` — cross-feature hooks (ShadCN convention). Empty so far.

### Styling & theme

`src/index.css` is Tailwind 4 (`@import "tailwindcss"`) + ShadCN variables in OKLCh with light/dark via a `.dark` class, plus Geist Variable font. Component variants use `class-variance-authority` (see `button.tsx`). Prefer ShadCN components + `cn()` over hand-rolled CSS.

### Env (`.env` in `frontend/`)

`VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_AUDIENCE`, `VITE_API_BASE_URL` (no scheme prefix — `apiFetch` concatenates as `${VITE_API_BASE_URL}${url}`, so the backend must accept the host without `http://` or the value must include it; verify before relying on it). These must match `backend/.env`'s `AUTH0_*` and the backend's host/port.

## Auth0 / env setup

`.env` (in `backend/`) holds `DB_`* and `AUTH0_*` values. The same Auth0 tenant/domain/clientId must match between `backend/.env` and `frontend/.env` (`VITE_AUTH0_*`). The backend expects custom claims namespaced by `AUTH0_AUDIENCE` (e.g. `https://fast-ticket.com/email`) — ensure the Auth0 API is configured to emit those claims. The frontend obtains the JWT with `getAccessTokenSilently()` (inside the api layer) and sends it as `Authorization: Bearer <token>` via `apiFetch`.