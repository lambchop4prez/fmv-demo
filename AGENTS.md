# AGENTS.md

## Setup & Dev Flow

- **Toolchain**: `mise` manages all runtime versions (Python 3.14.5, Node 24, uv, pnpm, lefthook). Run `mise install` after cloning.
- **Initial setup**: `just setup` — installs lefthook hooks, generates TLS certs via mkcert into `.cert/`.
- **Infra**: `just up infra` (MongoDB + RabbitMQ via docker-compose profiles). Full stack: `just up backend` or `just up frontend`.
- **Dev servers**: `just dev` (parallel: API + workers + frontend). Or individually: `just backend dev`, `just frontend dev`.
- **Down**: `just down infra` to teardown containers.

## Commands

| Command | What it does |
|---------|-------------|
| `just analyze` | Spellcheck + typecheck (parallel) + lint (parallel) — the CI gate |
| `just lint` | Frontend ESLint + backend ruff check/format (parallel) |
| `just typecheck` | `vue-tsc --noEmit` + `mypy .` (parallel) |
| `just spellcheck` | `typos` (excludes `ui/locales/*.yml`) |
| `just unit-test` | Vitest + pytest (parallel) |
| `just e2e` | Frontend WDIO e2e + collects container logs |
| `just ci` | `semantic-release` dry-run version bump |
| `just release` | `semantic-release` strict version (no commit) |
| `just publish` | Tag + push docker images |

Backend check commands run inside `src/` (via `just backend lint`, etc.). Frontend commands run inside `ui/` (via `just frontend lint`, etc.).

## Architecture

- **Backend** (`src/`): FastAPI app at `src/api/main.py` + Celery workers. Monorepo via `uv` workspace — `pyproject.toml` declares workspace members in `src/pkg/*` (config, models, service, repository, repository_mongodb, repository_inmemory, handlers, workers).
- **Frontend** (`ui/`): Vue 3 + Vite + shadcn-vue + UnoCSS. API client types are auto-generated from the OpenAPI spec.
- **Infra** (`docker-compose.yaml`): Services use docker profiles (`infra`, `backend`, `frontend`, `ci`). No traefik proxy currently (commented out).

## Gotchas

- **SSL/TLS required for dev**: The API dev server uses `--ssl-keyfile`/`--ssl-certfile` pointing to `.cert/`. Run `just setup` first, or certs won't exist.
- **Repository switch**: `BACKEND_REPOSITORY=mongodb` (default) vs `BACKEND_REPOSITORY=inmemory`. Controlled via `.mise.toml` env vars. The inmemory stub is useful for quick testing without MongoDB.
- **Env loading**: `.mise.toml` loads `{{config_root}}/.secrets.env` for runtime env vars. Create this file for local secrets.
- **API versioning**: Routers live at `src/api/v{n}/router.py` and are mounted in `src/api/main.py`. Within a version, only additive changes are allowed — breaking changes require a new versioned router.
- **Frontend codegen**: Run `just frontend gen-client` to regenerate `ui/src/client/api.d.ts` from the live OpenAPI spec at `http://localhost:8000/api/v1/openapi.json`.
- **Pre-commit hooks** (lefthook): actionlint, spellcheck, gitleaks, frontend lint (stage_fixed), backend lint, justfile formatting. Run `lefthook run pre-commit` manually.
- **Conventional Commits**: Required for `semantic-release`. Types: `feat`, `fix`, `test`, `build`, `ci`, `docs`, `style`, `refactor`, `perf`, `chore`. Scopes: `ui`, `api`, `workers`, `deps`. Use `!` before `:` for breaking changes.
- **No GitHub workflows yet**: `.github/` is empty. CI runs via `just ci` / `just publish` locally or in external CI.
- **Python 3.14.5 only**: `pyproject.toml` pins `==3.14.5`. Don't use a different version.
- **uv workspace**: Backend deps use `uv` with workspace members. Always run `uv sync` (or `just backend uv-sync-dev`) before running backend commands.

## Testing

- Backend: `uv run pytest` (run via `just backend unit-test`)
- Frontend unit: `pnpm run test:unit` (run via `just frontend unit-test`)
- Frontend e2e: `pnpm run test:e2e:dev` or `test:e2e:ci` (WDIO-based)
- E2E requires full infra + api + frontend running. Logs collected to `ui/test/logs/`.
