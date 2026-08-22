<!-- Context: project-intelligence/business | Priority: high | Version: 1.0 | Updated: 2026-06-19 -->

# Business Domain

> A full-stack demo project showcasing FastAPI, MongoDB, Vue 3, and Celery workers — themed around managing robots.

**Purpose**: Business context, project identity, and goals for this project.
**Last Updated**: 2026-06-19

## Quick Reference

- **Update When**: Project goals change, new features added, target audience shifts
- **Audience**: Developers, stakeholders, AI agents

## Project Identity

**Name**: FMV Demo (FastAPI + MongoDB + Vue)
**Tagline**: Full-stack demo showcasing modern Python + Vue development patterns
**Theme**: Robot management (MST3K-inspired naming: "Crow T. Robot", "Bender", "Satellite of Love")

## Problem Statement

This project demonstrates a complete full-stack application architecture:
- **Backend**: Async FastAPI REST API with versioned endpoints
- **Data**: MongoDB with Beanie ODM + in-memory fallback for testing
- **Async**: Celery workers for background task processing
- **Frontend**: Vue 3 SPA with auto-generated API types, shadcn-vue components
- **DevOps**: Docker Compose, mise for version management, just for task running

## Target Users

| User Type | Purpose |
|-----------|---------|
| Developers | Learn and reference full-stack patterns (FastAPI + Vue + MongoDB) |
| AI Agents | Receive project-specific context for code generation |
| Evaluators | Test CI/CD pipelines, code quality tools, and automation |

## Value Proposition

1. **Reference Architecture**: Complete, runnable full-stack app with real patterns (not toy code)
2. **Dev Experience**: `just setup` + `just dev` — minimal commands to get started
3. **Code Quality**: Strict typing (mypy, vue-tsc), linting (ruff, ESLint), spellcheck
4. **Testing**: Unit tests (pytest + Vitest) + E2E tests (WDIO)
5. **CI/CD Ready**: semantic-release for versioning, Docker publishing pipeline

## Success Metrics

- [ ] `just analyze` passes (lint + typecheck + spellcheck)
- [ ] `just unit-test` passes (backend + frontend)
- [ ] `just e2e` passes (full stack in Docker)
- [ ] `just ci` runs semantic-release dry-run successfully
- [ ] New developers can run `just dev` and access the app

## Business Model

This is a **demo/reference project** — not a commercial product. Its purpose is:
- Showcase modern full-stack development patterns
- Provide a testbed for CI/CD and code quality tooling
- Serve as context source for AI agents working on similar projects

## Constraints

- Python pinned to 3.14.5 (no version drift)
- API versioning: additive-only changes per version
- Docker-based infrastructure (no local installs for infra)
- TLS required for all dev servers (HTTPS-only)
- Conventional Commits required for semantic-release

## Roadmap

| Status | Item |
|--------|------|
| ✅ | In-memory database stub |
| ✅ | MongoDB database adapter |
| ✅ | Complete docker-compose file |
| ✅ | Unit/E2E testing |
| 🔄 | API Authentication (OAuth2/OIDC) |

## 📂 Codebase References

**README**: `README.md` — Project overview and getting started
**Contributing**: `CONTRIBUTING.md` — Development guide and commit conventions
**Backend**: `src/README.md` — Backend architecture and layout
**Frontend**: `ui/README.md` — Frontend tooling and component structure
**Justfile**: `.justfile` — All build/dev/test/release commands

## Related Files

- Technical Domain (`technical-domain.md`) — How this project is built
- Decisions Log (`decisions-log.md`) — Why key decisions were made
- Living Notes (`living-notes.md`) — Active issues and open questions
