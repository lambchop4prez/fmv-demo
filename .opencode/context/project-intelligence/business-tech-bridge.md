<!-- Context: project-intelligence/bridge | Priority: medium | Version: 1.0 | Updated: 2026-06-19 -->

# Business-Tech Bridge

> How business needs map to technical solutions in this project.

**Purpose**: Connect business requirements to technical implementation.
**Last Updated**: 2026-06-19

## Quick Reference

- **Update When**: New features added, architecture changes, business goals shift
- **Audience**: Developers, stakeholders, AI agents

## Core Mapping

| Business Need | Technical Solution | Implementation |
|--------------|-------------------|----------------|
| Fast, reliable API | FastAPI + async endpoints | `src/api/v1/endpoints/` |
| Flexible data storage | MongoDB + Beanie ODM | `src/pkg/repository_mongodb/` |
| Quick testing without DB | In-memory repository | `src/pkg/repository_inmemory/` |
| Background processing | Celery workers + RabbitMQ | `src/pkg/workers/` |
| Type-safe frontend | OpenAPI codegen + TypeScript | `ui/src/client/api.d.ts` |
| Consistent UI components | shadcn-vue + UnoCSS | `ui/src/components/ui/` |
| Dev environment parity | Docker Compose + TLS | `docker-compose.yaml`, `.cert/` |
| Automated releases | semantic-release + Conventional Commits | `.config/release.toml` |

## Feature Mapping

### Robot CRUD Operations

```
Business: Manage robot records
  ├─ List robots     → GET  /api/v1/robot/     → robot.list()
  ├─ Create robot    → POST /api/v1/robot/     → robot.create()
  ├─ Get robot       → GET  /api/v1/robot/{name} → robot.find()
  └─ Run robot task  → POST /api/v1/robot/{name}/run → Celery task
```

**Data Flow**:
1. Frontend calls `client.GET('/robot/')` (type-safe from OpenAPI)
2. FastAPI endpoint receives request, injects `RobotServiceDep`
3. Service calls `RobotRepository.list()` (Protocol-based)
4. MongoDB impl returns `Sequence[Robot]` via Beanie
5. Response serialized to JSON, returned to frontend

### Async Task Execution

```
Business: Run long-running computation without blocking API
  └─ POST /api/v1/robot/{name}/run
      → Service calls Celery `primes()` task
      → Task published to RabbitMQ
      → Worker picks up task, executes in handlers
      → Result stored in MongoDB (taskmeta_collection)
```

## Trade-off Decisions

| Decision | Trade-off | Why Chosen |
|----------|-----------|------------|
| MongoDB over PostgreSQL | Less relational integrity | Document model fits Robot schema; simpler setup |
| Protocol over ABC for Repository | Less explicit error messages | Structural typing is more flexible; no inheritance needed |
| OpenAPI codegen over manual types | Build step required | Eliminates type drift; single source of truth |
| Docker profiles over single compose | Slightly more complex | Selective service startup saves resources |
| uv over pip/poetry | Newer ecosystem | Faster installs; workspace support; growing adoption |

## Common Misalignments

| Business Expectation | Technical Reality | Resolution |
|---------------------|-------------------|------------|
| "Just add a feature" | API versioning requires additive-only changes | New endpoints ok; breaking changes need v2 |
| "Test without Docker" | Infra requires MongoDB + RabbitMQ | Use `BACKEND_REPOSITORY=inmemory` for stub |
| "Frontend types match backend" | Types must be regenerated after API changes | Run `just frontend gen-client` after changes |
| "Local dev = production" | TLS required locally for browser APIs | `just setup` generates mkcert certs |

## Stakeholder Communication

| Stakeholder | What They Need | Where to Find It |
|-------------|---------------|------------------|
| Developers | How to run, test, deploy | `CONTRIBUTING.md`, `technical-domain.md` |
| AI Agents | Project patterns, conventions | `.opencode/context/project-intelligence/` |
| Evaluators | CI/CD pipeline, quality gates | `.justfile`, `AGENTS.md` |
| Reviewers | Architecture decisions | `decisions-log.md` |

## 📂 Codebase References

**API Endpoints**: `src/api/v1/endpoints/robot.py` — CRUD + task execution
**Service Layer**: `src/pkg/service/` — business logic between API and repository
**Repository**: `src/pkg/repository/src/repository/` — Protocol interface
**MongoDB Impl**: `src/pkg/repository_mongodb/src/repository_mongodb/` — Beanie ODM
**Celery Worker**: `src/pkg/workers/src/workers/tasks.py` — async task definitions
**Frontend Client**: `ui/src/lib/index.ts` — openapi-fetch typed client
**Frontend Pages**: `ui/src/pages/robot/` — robot CRUD UI

## Related Files

- Technical Domain (`technical-domain.md`) — Full architecture details
- Business Domain (`business-domain.md`) — Project goals and constraints
- Decisions Log (`decisions-log.md`) — Rationale for key decisions
