<!-- Context: project-intelligence/decisions | Priority: high | Version: 1.0 | Updated: 2026-06-19 -->

# Decisions Log

> Major technical and architectural decisions with context, rationale, and alternatives.

**Purpose**: Record why key decisions were made for future reference.
**Last Updated**: 2026-06-19

## Quick Reference

- **Update When**: New architectural decisions are made
- **Audience**: Developers, AI agents, reviewers

## Active Decisions

### 1. Python Package Management with uv Workspace

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Need a fast, modern Python package manager with workspace support |
| **Decision** | Use `uv` with workspace members in `src/pkg/*` |
| **Rationale** | uv is significantly faster than pip/poetry. Workspace members allow clean separation of concerns (models, repository, service, workers) while sharing dependencies. |
| **Alternatives** | poetry, pip-tools, pdm |
| **Impact** | All backend deps managed via `uv sync`. Each pkg member has its own pyproject.toml. |

**Refs**: `pyproject.toml`, `src/pkg/*/pyproject.toml`

---

### 2. Repository Pattern with Python Protocol

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Need swappable data access layer (MongoDB vs in-memory) |
| **Decision** | Define `RobotRepository` as a `Protocol` in `repository/` package, with separate implementations in `repository_mongodb/` and `repository_inmemory/` |
| **Rationale** | Protocol-based typing (PEP 544) provides structural subtyping without inheritance. Switching implementations is a single env var (`BACKEND_REPOSITORY`). No DI framework needed. |
| **Alternatives** | ABC (abstract base class), explicit interface classes, dependency injection container |
| **Impact** | Clean separation of interface from implementation. Easy to add new repository types. |

**Refs**: `src/pkg/repository/src/repository/robot.py`, `src/pkg/repository_mongodb/src/repository_mongodb/robot.py`

---

### 3. API Versioning via URL Prefix

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Need to evolve API without breaking existing clients |
| **Decision** | Versioned routers at `/api/v{n}/` with additive-only changes per version |
| **Rationale** | URL-based versioning is explicit, cacheable, and easy to route. Breaking changes require a new version (v2, v3, etc.). |
| **Alternatives** | Header-based versioning, query param versioning, content negotiation |
| **Impact** | `src/api/v1/api.py` is a separate FastAPI app mounted at `/api/v1`. New versions get their own `v2/`, `v3/` directories. |

**Refs**: `src/api/main.py`, `src/api/v1/api.py`, `src/api/v1/router.py`

---

### 4. Celery Workers with MongoDB Backend

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Need async task processing for long-running operations |
| **Decision** | Celery with RabbitMQ broker + MongoDB result backend |
| **Rationale** | RabbitMQ is reliable for task distribution. MongoDB as result backend avoids needing Redis. Task metadata stored alongside app data. |
| **Alternatives** | Redis broker + backend, Celery with RPC backend, asyncio tasks |
| **Impact** | Workers run as separate Docker service. Tasks defined in `workers/tasks.py`, handlers in `handlers/`. |

**Refs**: `src/pkg/workers/src/workers/tasks.py`, `src/pkg/workers/src/workers/task_config.py`, `docker-compose.yaml`

---

### 5. Frontend API Types Auto-Generated from OpenAPI

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Need type-safe frontend API calls without manual type maintenance |
| **Decision** | Generate TypeScript types from FastAPI OpenAPI spec using `@hey-api/openapi-ts` |
| **Rationale** | Single source of truth (FastAPI Pydantic models → OpenAPI → TypeScript types). No drift between backend and frontend types. |
| **Alternatives** | Manual TypeScript interfaces, tRPC, GraphQL |
| **Impact** | Run `just frontend gen-client` after API changes. Types in `ui/src/client/api.d.ts`. |

**Refs**: `ui/package.json` (client:gen script), `ui/src/client/api.d.ts`

---

### 6. TLS Required for All Dev Servers

| Field | Value |
|-------|-------|
| **Date** | 2026-06-19 |
| **Status** | Active |
| **Context** | Some browser APIs (Web Crypto, Service Workers) require HTTPS |
| **Decision** | Generate self-signed TLS certs via mkcert, serve all dev servers over HTTPS |
| **Rationale** | mkcert creates trusted local certs. Avoids browser security warnings. Required for full feature parity with production. |
| **Alternatives** | HTTP-only dev, self-signed certs accepted manually |
| **Impact** | `just setup` generates certs into `.cert/`. FastAPI dev server uses `--ssl-keyfile`/`--ssl-certfile`. Vite server configured with HTTPS in `vite.config.ts`. |

**Refs**: `.justfile` (setup target), `ui/vite.config.ts` (server.https), `.mise.toml` (VITE_DEV_CERT)

---

## Deprecated Decisions

| Decision | Replaced By | Reason |
|----------|-------------|--------|
| Traefik proxy | None (commented out) | Not needed for current dev setup |

## 📂 Codebase References

**API Versioning**: `src/api/main.py` — mounts versioned routers
**Repository Switch**: `src/api/main.py` (lifespan) — checks `settings.repository`
**Celery Config**: `src/pkg/workers/src/workers/task_config.py` — MongoDB result backend
**Frontend Client**: `ui/src/lib/index.ts` — openapi-fetch client setup
**TLS Setup**: `.justfile` (setup target), `ui/vite.config.ts` (server.https)

## Related Files

- Technical Domain (`technical-domain.md`) — Current architecture
- Business Domain (`business-domain.md`) — Project goals and constraints
