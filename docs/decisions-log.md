# Decisions Log — Authentication (OIDC)

> **This file is the authoritative decisions log for authentication in this
> project.** General project-wide architecture decisions live in
> `.opencode/context/project-intelligence/decisions-log.md` (referenced below
> as "project log"). Auth decisions recorded here override nothing there;
> they extend it.

**Source**: `docs/oidc-plan.md` (D1–D7), owner-approved 2026-09-05
(session `.tmp/sessions/2026-09-05-oidc-auth/context.md`).
**Last Updated**: 2026-09-05

## Quick Reference

| ID | Decision | Status |
|----|----------|--------|
| D1 | Session cookie auth; bearer only at `POST /auth/login` | Active |
| D2 | JWKS validation, two key sources behind one resolver (static / network) | Active |
| D3 | Per-provider `role_claims` + `api/scopes.py` scope constants | Active |
| D4 | Frontend uses `oidc-client-ts` `UserManager`, in-memory tokens | Active |
| D5 | Auth shape fixes land in v1 (unreleased, no consumers) | Active |
| D6 | Static-key stub + tiny mock IdP container for dev/e2e | Active |
| D7 | Per-provider `verify_ssl: bool = True`, never default off | Active |

## Decisions

### D1 — Session cookie, bearer only at login

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | (a) Session cookie. All protected routes read `request.session["user"]`. Bearer only at `POST /auth/login`. Scopes/roles stored in session at login. |
| **Rationale** | The browser never holds a long-lived API token. The IdP `id_token` is exchanged once for an HttpOnly, Secure, SameSite=strict session cookie. This shrinks the XSS token-theft surface and keeps protected-route auth to one cookie check. |
| **Consequence** | `/auth/login` is the only bearer-consuming route. `get_current_user` returns 401 with no session user; `require_scope` returns 403 when the session lacks the scope. `rotate_session` clears and repopulates `request.session` — the middleware owns the cookie. CORS needs `CORS_ALLOW_CREDENTIALS=true` with explicit origins. |

**Refs**: `src/api/v1/endpoints/auth.py`, `src/api/v1/dependencies/auth.py`, `.mise.toml`

### D2 — JWKS validation with two key sources behind one resolver

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | JWKS validation with two key sources behind one resolver: `static_jwks` set (dev/CI) selects the key by token header `kid` from the static set; otherwise a cached `PyJWKClient` fetches from the provider `jwks_url`. Introspection is documented as the future upgrade path only. |
| **Rationale** | Dev and CI must validate tokens offline — no live IdP required. One resolver keeps the validation path identical in both modes; the key source is a per-provider config choice, not a code branch in the dependency. |
| **Consequence** | `OidcProviderSettings` gains `static_jwks` / `static_jwks_file`. Startup fails closed: `static_jwks` is rejected when `BACKEND_ENVIRONMENT=production`. Test keypair fixtures carry the public key (safe to commit, documented loudly). |

**Refs**: `src/pkg/config/src/config/oidc.py`, `.secrets.env.example` (`STATIC_JWKS` note)

### D3 — Per-provider role claims + scope constants

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | Per-provider `role_claims` config plus `api/scopes.py` scope constants; endpoints declare required scopes in code. |
| **Rationale** | Each IdP names its roles claim differently (`groups`, `roles`, …). A per-provider setting keeps the mapping out of endpoint code. Constants in one module make required scopes greppable and reviewable per route. |
| **Consequence** | `OIDC__PROVIDERS__<NAME>__ROLE_CLAIMS` env per provider. New protected endpoints declare scopes explicitly; missing scope means 403. |

**Refs**: `src/api/v1/scopes.py` (new), `docs/oidc-plan.md` §4.2

### D4 — Frontend: oidc-client-ts UserManager, in-memory tokens

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | `oidc-client-ts` `UserManager`, in-memory access token + silent renew; session cookie for API calls. Callback POSTs the `id_token` to `/auth/login`. |
| **Rationale** | Matches the existing `useUserManager()` call sites (`LoginForm.vue`, `callback.vue`, `logout.vue`). In-memory storage (`InMemoryWebStorage`) keeps IdP tokens out of localStorage. The API never sees bearer tokens after login (D1). |
| **Consequence** | `ui/src/composables/auth.ts` exports `useUserManager` + `useUserManagerSettings`, driven by `VITE_OIDC_*` env vars from `.mise.toml`. `ui/src/lib/index.ts` sends `credentials: 'include'`. |

**Refs**: `ui/src/composables/auth.ts`, `ui/src/lib/index.ts`, `.mise.toml`

### D5 — Fix auth in v1

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | Fix in v1 (auth unreleased; no consumers yet). Allowed by the CONTRIBUTING.md additive-rule interpretation agreed by the owner. |
| **Rationale** | Project log #3 says v1 changes must be additive and breaking changes require a new version. Auth endpoints were never released and no client consumes the current shapes, so fixing response shapes and config in v1 carries no breakage risk. |
| **Consequence** | `/auth/login`, `/auth/logout` and OIDC config may change shape in v1. Once auth ships, the additive-only rule applies strictly and breaking changes require a v2 router. |

**Refs**: `CONTRIBUTING.md`, `.opencode/context/project-intelligence/decisions-log.md` (#3)

### D6 — Static-key stub + tiny mock IdP container for e2e

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | Static-key stub + tiny mock IdP container for the e2e redirect flow. NOT Keycloak. A ~100-line FastAPI mock IdP in the `ci`/`infra` compose profile serves `.well-known/openid-configuration`, `.well-known/jwks.json` (static public key), and a login page that redirects with a token signed by the test private key. |
| **Rationale** | Keycloak is heavy, slow to boot, and unnecessary for contract testing. A minimal mock keeps e2e hermetic, offline, and reproducible, while exercising the real redirect + JWKS contract. |
| **Consequence** | Dev issuer is `https://localhost:8443/realms/fmv` — coupled in `.mise.toml` (`VITE_OIDC_AUTHORITY`) and `.secrets.env.example` (`OIDC__PROVIDERS__KEYCLOAK__ISSUER`). The provider name `keycloak` is a legacy label kept for config stability; the container is not Keycloak. |

**Refs**: `docker-compose.yaml` (task 06), `.mise.toml`, `.secrets.env.example`

### D7 — verify_ssl per provider, never default off

| Field | Value |
|-------|-------|
| **Date** | 2026-09-05 |
| **Status** | Active (owner-approved) |
| **Decision** | `verify_ssl: bool = True` per provider, kept for real-IdP mode. Moot in static mode (no network). Never default off. |
| **Rationale** | TLS verification against a real IdP must stay on by default so a forgotten flag cannot silently disable certificate checks. The self-signed dev mock IdP opts out explicitly via env. |
| **Consequence** | `OIDC__PROVIDERS__<NAME>__VERIFY_SSL=false` appears only in dev config (`.secrets.env.example`). Production configs omit it, so the default `true` applies. |

**Refs**: `src/pkg/config/src/config/oidc.py`, `.secrets.env.example`

## Related Files

- `docs/oidc-plan.md` — master plan (defects, architecture, phases)
- `.tmp/sessions/2026-09-05-oidc-auth/context.md` — session context, owner decisions verbatim
- `.opencode/context/project-intelligence/decisions-log.md` — project-wide decisions (#1–#6)
