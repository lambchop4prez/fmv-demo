<!-- Context: project-intelligence/living | Priority: medium | Version: 1.0 | Updated: 2026-06-19 -->

# Living Notes

> Active issues, technical debt, open questions, and lessons learned.

**Purpose**: Track the current state of the project and things to watch.
**Last Updated**: 2026-06-19

## Quick Reference

- **Update When**: New issues arise, debt is addressed, lessons are learned
- **Audience**: Developers, AI agents

## Technical Debt

| Item | Impact | Priority |
|------|--------|----------|
| Traefik proxy commented out in docker-compose | No reverse proxy for local dev | Low |
| No GitHub workflows (`.github/` is empty) | CI runs locally only via `just ci` | Medium |
| Authentication implemented but not enabled | JWT/PyJWT installed, session middleware exists, but auth endpoints not active | High |

## Open Questions

| Question | Context | Status |
|----------|---------|--------|
| Should API v2 be planned now? | v1 is stable, but OAuth2/OIDC may require breaking changes | Open |
| Redis vs MongoDB for Celery result backend? | MongoDB works but Redis is the Celery default | Open |
| SSR vs SSG for frontend? | Currently using vite-ssg (static generation) | Open |

## Known Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| Python 3.14 pin | Must use exactly 3.14.5, no other version | Use `mise` for version management |
| TLS cert regeneration | `.cert/` must exist before dev servers start | Run `just setup` first |

## Insights & Lessons Learned

- **uv workspace members** provide clean separation without complex build configs
- **Protocol-based repositories** work well for swappable data layers in Python
- **OpenAPI codegen** eliminates frontend/backend type drift
- **mise + just** combination handles both runtime versions and task running elegantly
- **Docker profiles** allow selective service startup (infra only, backend only, etc.)

## Patterns & Conventions

- Always use `async def` for FastAPI endpoints
- Repository Protocol lives in `repository/`, implementations in `repository_*`
- Frontend composables auto-imported — no explicit `import { useX }` needed
- Vue pages use `<route lang="yaml">` meta blocks for layout assignment
- All env vars loaded from `.mise.toml` → `.secrets.env` chain

## Active Projects

| Project | Description | Status |
|---------|-------------|--------|
| API Authentication | OAuth2/OIDC implementation | In Progress |

## Archive

| Item | Resolved | Notes |
|------|----------|-------|
| Project-context.md deprecation | Yes | Replaced by project-intelligence/ structure |

## 📂 Codebase References

**Auth endpoints**: `src/api/v1/endpoints/auth.py` — implemented but not enabled
**Celery tasks**: `src/pkg/workers/src/workers/tasks.py` — prime computation task
**Docker profiles**: `docker-compose.yaml` — infra, backend, frontend, ci
**Version pinning**: `.mise.toml` — Python 3.14.5, Node 24.16.0

## Related Files

- Technical Domain (`technical-domain.md`) — Current architecture
- Decisions Log (`decisions-log.md`) — Why decisions were made
