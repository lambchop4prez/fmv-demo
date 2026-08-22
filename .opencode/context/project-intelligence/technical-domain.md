<!-- Context: project-intelligence/technical | Priority: critical | Version: 1.1 | Updated: 2026-06-19 -->

# Technical Domain

> FastAPI + MongoDB + Vue 3 full-stack demo with Celery workers. Monorepo managed by `uv` (Python) and `pnpm` (frontend).

**Purpose**: Tech stack, architecture, and development patterns for this project.
**Last Updated**: 2026-06-19

## Quick Reference

- **Update When**: Tech stack changes, new API version, architecture decisions
- **Audience**: Developers, AI agents

## Primary Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | 3.14.5 | Type-safe backend, pinned in pyproject.toml |
| Backend Framework | FastAPI | 0.136.1 | Async, auto OpenAPI, Pydantic integration |
| Frontend Framework | Vue 3 | catalog | Reactive, composable, strongly typed |
| Database | MongoDB | latest | Document store via Beanie ODM |
| Message Broker | RabbitMQ | 4-management | Celery task queue |
| Package Manager (Python) | uv | 0.11.16 | Fast workspace-based Python deps |
| Package Manager (JS) | pnpm | 11.2.2 | Frontend deps with catalogs |
| Task Runner | just | 1.51.0 | Cross-platform build/dev commands |
| Styling | UnoCSS + shadcn-vue | catalog | Atomic CSS + component library |

## Architecture Pattern

```
Type: Monolith (backend) + SPA (frontend)
Pattern: API versioned at /api/v1/ + Celery async workers
```

FastAPI provides sync API + Celery handles async tasks. MongoDB stores app data and Celery task metadata. Frontend is a separate Vue SPA consuming the REST API.

## Project Structure

```
.
├── src/api/              # FastAPI app (main.py, v1/ routers, endpoints/)
├── src/pkg/              # uv workspace: config, models, repository, service, workers
├── ui/src/               # Vue SPA (pages/, components/, composables/, stores/)
├── docker-compose.yaml   # Services (profiles: infra, backend, frontend, ci)
├── pyproject.toml        # Python workspace root
└── .mise.toml            # Runtime versions + env vars
```

**Key dirs**: `src/api/v1/endpoints/` (route handlers), `src/pkg/models/` (Pydantic), `src/pkg/repository/` (Protocol interface), `ui/src/composables/` (reusable logic), `ui/src/components/ui/` (shadcn-vue).

## Code Patterns

### Backend API Endpoint

```python
# src/api/v1/endpoints/robot.py
@router.get("/")
async def list(service: RobotServiceDep) -> RobotCollection:
    return RobotCollection(robots=await service.list())

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(service: RobotServiceDep, robot: RobotProfile = Body(...)) -> RobotProfile:
    await service.create(robot)
    return robot
```

**Rules**: `async def` for all endpoints, inject deps via FastAPI `Depends`, return Pydantic models directly, raise `HTTPException` for errors, business logic in `service/` layer.

### Repository Pattern (Protocol-based)

```python
# src/pkg/repository/src/repository/robot.py
class RobotRepository(Protocol):
    @abstractmethod
    async def list(self) -> Sequence[Robot]: ...
    async def create(self, robot: RobotProfile) -> None: ...
    async def find(self, name: str) -> RobotProfile | None: ...
```

Interface in `repository/` (Protocol), implementations in `repository_mongodb/` and `repository_inmemory/`. Switch via `BACKEND_REPOSITORY` env var.

### Frontend Composable Pattern

```typescript
// ui/src/composables/robotList.ts
export function useRobotList(fetchOptions) {
  const state = ref<RobotListResponse>();
  const isReady = ref(false);
  const isFetching = ref(false);
  const error = ref<AppError | undefined>(undefined);
  async function execute() { /* fetch via openapi-fetch */ }
  return { state, isReady, isFetching, error, execute };
}
```

Composables auto-imported via `unplugin-auto-import`. Return reactive refs + action functions. Use `~/client/api` for type-safe API types (auto-generated from OpenAPI).

### Frontend Component Pattern

```vue
<!-- ui/src/components/RobotItem.vue -->
<script setup lang="ts">
import type { components } from '~/client/api';
const props = defineProps<{ robot: components['schemas']['Robot'] }>();
</script>
<template><Item><ItemContent><ItemTitle>{{ props.robot.name }}</ItemTitle></ItemContent></Item></template>
```

`<script setup lang="ts">` with `defineProps` using auto-generated API types. shadcn-vue components auto-imported. UnoCSS utility classes on components. Pages use `<route lang="yaml">` meta blocks.

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Python files/modules | snake_case | `robot_profile.py`, `repository_mongodb/` |
| Python classes | PascalCase | `RobotProfile`, `MongoDbRobotRepository` |
| Python functions | snake_case | `list()`, `find()`, `primes()` |
| Vue files | PascalCase | `RobotItem.vue`, `RobotForm.vue` |
| Vue pages | kebab-case/param | `index.vue`, `[name].vue`, `new.vue` |
| TypeScript files | camelCase | `robotList.ts`, `robotProfile.ts` |
| API routes | kebab-case | `/robot/`, `/auth/` |
| Database fields | snake_case | `is_great`, `task_id` |
| Env vars | UPPER_SNAKE_CASE | `BACKEND_REPOSITORY`, `VITE_API_ENDPOINT` |

## Code Standards

- **Python**: `mypy` strict mode (`disallow_untyped_defs`, `disallow_any_unimported`)
- **Python linting**: `ruff` (check + format)
- **TypeScript**: `vue-tsc --noEmit`
- **Frontend linting**: ESLint with `@vue/eslint-config-typescript`
- **Testing**: pytest (backend) + Vitest (frontend) + WDIO (e2e)
- **Python workspace**: `uv` with workspace members in `src/pkg/*`
- **Pre-commit**: lefthook (actionlint, spellcheck, gitleaks, lint)
- **Python version**: pinned to `==3.14.5` — never use a different version
- **API versioning**: additive-only within a version; breaking changes require new versioned router

## Security Requirements

- TLS/SSL required for dev (`.cert/` via mkcert)
- CORS configured via `cors_settings`
- Session middleware with `https_only=True` in production
- Input validation via Pydantic (backend) and Zod (frontend forms)
- Parameterized queries via Beanie ODM (no raw MongoDB queries)
- Gitleaks pre-commit hook for secret detection
- JWT/PyJWT for authentication (implemented but not yet enabled)

## Development Environment

```bash
mise install          # Install runtime versions
just setup            # Install lefthook + generate TLS certs
just up infra         # Start MongoDB + RabbitMQ
just dev              # Start API + workers + frontend
```

**Key env vars**: `BACKEND_REPOSITORY=mongodb` (switch to `inmemory` for testing), `BACKEND_MONGO_DATABASE=robot`, `VITE_API_ENDPOINT=https://localhost:8000/api/v1`.

## Deployment

- Docker images: `ghcr.io/lambchop4prez/fmv-demo-{backend,frontend}`
- Docker profiles: `infra`, `backend`, `frontend`, `ci`
- CI/CD: `semantic-release` (conventional commits → version bumps)
- Build: `just build` → `just publish` (tag + push images)

## 📂 Codebase References

**API Entry**: `src/api/main.py` — FastAPI app with lifespan, versioned router mounting
**API Router**: `src/api/v1/router.py` — Composes endpoint routers (auth, robot, util)
**Models**: `src/pkg/models/src/models/` — Pydantic models (Robot, RobotProfile, RobotTask, User)
**Repository Interface**: `src/pkg/repository/src/repository/robot.py` — Protocol-based data access
**MongoDB Impl**: `src/pkg/repository_mongodb/src/repository_mongodb/robot.py` — Beanie ODM
**Celery Tasks**: `src/pkg/workers/src/workers/tasks.py` — Celery worker + task definitions
**Frontend Composables**: `ui/src/composables/` — useRobotList, useRobotProfile, useDark
**Frontend Components**: `ui/src/components/` — shadcn-vue + custom (RobotItem, RobotForm)
**Frontend Pages**: `ui/src/pages/` — file-based routing (robot/index.vue, robot/new.vue)
**Config**: `.mise.toml` — runtime versions + env vars, `pyproject.toml` — Python workspace
**Docker**: `docker-compose.yaml` — service definitions with profiles

## Related Files

- Business Domain (`business-domain.md`) — Why this technical foundation exists
- Decisions Log (`decisions-log.md`) — Major technical decisions with rationale
- Project Intelligence Standard (`.opencode/context/core/standards/project-intelligence.md`)
