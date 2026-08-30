# OIDC Authentication Plan

**Status**: Draft — awaiting owner decisions (D1–D7)
**Created**: 2026-08-29
**Verified against**: `main` @ `3f5bbe8`
**Purpose**: Standalone plan to finish OIDC authentication in this repo. Written for a fresh session. No prior conversation context is required to execute it.

## How to pick this up

1. Read this document fully.
2. Load project context before writing code:
   - `.opencode/context/core/standards/code-quality.md`
   - `.opencode/context/core/standards/security-patterns.md`
   - `.opencode/context/development/principles/api-design.md`
   - `.opencode/context/project-intelligence/decisions-log.md` (Decision #3 governs API versioning)
3. Confirm decisions D1–D7 (section 3) with the project owner. Do not implement before D1 and D3 are answered.
4. Execute phases in order (section 6).

---

## 1. Goal

- Configurable OIDC login for the Vue frontend and protected FastAPI endpoints.
- One identity provider (IdP) at launch. Multi-IdP support must not require a
  breaking config change later — model providers as a collection now, single
  provider is the n=1 case.
- The template must boot and pass `just analyze` + `just e2e` on a clean clone
  with only `.secrets.env` filled in.

## 2. Current state (verified at `3f5bbe8`)

Auth is half-landed. Facts below were checked against the committed tree.

| File | State |
|------|-------|
| `src/pkg/config/src/config/oidc.py` | Flat single-provider settings. `issuer`, `audience`, `signing_key_id` required at import. No multi-provider support. |
| `src/pkg/config/src/config/session.py` | `secret_key` required at import. Cookie flags OK. |
| `src/pkg/config/src/config/cors.py` | `allow_credentials` defaults `False`. Never set in `.mise.toml`. |
| `src/api/v1/dependencies/auth.py` | Token validation exists but has 4 defects (below). |
| `src/api/v1/endpoints/auth.py` | `POST /auth/login`, `POST /auth/logout` exist. Login has defects (below). |
| `src/api/v1/middleware.py` | `CORSMiddleware` + `SessionMiddleware` wired. |
| `src/api/v1/endpoints/robot.py` | No auth dependency on any route. |
| `ui/src/composables/auth.ts` | **Missing from git.** `auto-imports.d.ts` declares `useUserManager`; `LoginForm.vue`, `callback.vue`, `logout.vue` call it. Runtime `ReferenceError`. |
| `ui/package.json` | No OIDC client library (`oidc-client-ts`) installed. |
| `ui/src/lib/index.ts` | openapi-fetch client has no `credentials: 'include'`. Session cookie never sent cross-origin. |
| `docker-compose.yaml` | `api` service env declares only `SERVER_*`, `BACKEND_MONGO_*`, `BACKEND_REPOSITORY`. No `SESSION_*` or `OIDC_*`. |

### Backend defects (must fix)

1. **`decode_complete` shape bug** — `validate_token` returns
   `jwt.decode_complete()` output (`{"header", "payload", "signature"}`).
   `validate_scope` reads `token.get(role_claims)` at top level, so claims are
   always `None` → HTTP 400 on every scoped route. Return `decoded["payload"]`
   from `validate_token` and adapt `login_session` accordingly.
2. **Static `signing_key_id`** — key selected by config, not by the token's
   header `kid`. Breaks on IdP key rotation: `keyset[kid]` raises `KeyError`
   (not an `InvalidTokenError`), escaping the `except` → HTTP 500. Use
   `jwks_client.get_signing_key_from_jwt(token)` and delete `signing_key_id`
   from config.
3. **`PyJWKClient` built per request** — `Depends(jwks_client)` constructs a
   new client each request, defeating its built-in key-set cache. Build one
   client per provider once (app state / module cache).
4. **TLS verification disabled globally** — `check_hostname=False` +
   `CERT_NONE` on the JWKS fetch lets a network-position attacker serve a
   forged key set. Default must be verify-on, with an explicit dev-only flag
   (see D7).
5. **Login 500 on missing claims** — `User(**payload)` requires
   `name`/`picture`/`email`/`email_verified`. IdPs that omit these claims
   crash first login. Make `User` fields optional with defaults, or map
   claims defensively.
6. **Soft-deleted users re-auth silently** — `MongoDbUserRepository.remove`
   sets `active=False`, but `login_session` never checks `active` for existing
   users. Add the check at login.
7. **`rotate_session` dead code** — it manually sets a cookie valued
   `request.session.get("_session_id", ...)`. Starlette `SessionMiddleware`
   has no `_session_id`; the middleware overwrites the cookie after the handler
   returns. Remove the manual `set_cookie`; rely on the middleware. Also
   decouple `httponly` from `https_only` (auth.py:35).

### Settings-at-import

`oidc_settings` / `session_settings` / `cors_settings` instantiate at module
import. Any import of `api` then requires secrets, which breaks clean-clone
CI. Replace module-level singletons with `@lru_cache` factory functions and
conftest defaults.

## 3. Decision points — review before implementing

These are the places the previous approach may change. Owner input required.

**D1 — Browser auth model.** Current code mixes bearer tokens and session
cookies. Options:
- (a) **Session cookie for UI routes; bearer only at `POST /auth/login`**
  (token→session exchange). Recommended: keeps IdP tokens out of browser
  storage for API calls, gives server-side revocation, works with
  `credentials: 'include'`.
- (b) Bearer pass-through on every route. Simpler, but exposes IdP tokens to
  frontend storage/XSS surface and makes logout/revocation client-dependent.

**D2 — Validation strategy.** Local JWKS validation (current) vs token
introspection (commented-out stub in `endpoints/auth.py`). Recommended: JWKS
for the template; document introspection as the upgrade path when revocation
within token lifetime is required.

**D3 — Claims → scopes mapping.** `validate_scope` compares
`security_scopes.scopes` against the raw `role_claims` list. Decide the
contract: does the IdP issue scopes directly (`scope` claim), or do groups map
to scopes via a static map? Recommended: per-provider `role_claims` plus an
explicit scope constant module (`api/scopes.py`), so endpoint decorators declare
required scopes in code.

**D4 — Frontend token handling.** `oidc-client-ts` with `UserManager`
(matches existing `useUserManager` call sites). Decide storage: recommended
in-memory access token + silent renew, session cookie for API calls. Confirm
the callback → `POST /auth/login` exchange contract.

**D5 — API versioning.** `/auth/login` and `/auth/logout` exist in v1. Per
decisions-log #3, v1 changes must be additive. Fixing response shapes
(e.g. what `/auth/login` returns) may be breaking → decide: adjust within v1
while the feature is unreleased, or mount `/auth` in v2. Recommended: fix in
v1 now, since no client consumes it yet.

**D6 — Dev/e2e IdP.** Nothing in compose provides an OIDC issuer today.
Options: Keycloak sidecar in the `infra` profile with a realm export fixture
(recommended — offline, reproducible), or point dev at a real cloud IdP.

**D7 — TLS verification flag.** Add `verify_ssl: bool = True` per provider
(env `OIDC__PROVIDERS__<NAME>__VERIFY_SSL=false` for a self-signed dev IdP
only). Never default to off.

## 4. Target architecture

### 4.1 Config (multi-IdP)

```python
# src/pkg/config/src/config/oidc.py
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class OidcProviderSettings(BaseModel):
    issuer: str
    audience: str
    client_id: str | None = None
    role_claims: str = "groups"
    jwks_cache_seconds: int = 300
    verify_ssl: bool = True

    @property
    def oidc_url(self) -> str:
        return f"{self.issuer}/.well-known/openid-configuration"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"


class OpenIdConnectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OIDC_",
        env_nested_delimiter="__",
        extra="allow",
    )
    providers: dict[str, OidcProviderSettings]
    default_provider: str | None = None

    @property
    def provider_names(self) -> list[str]:
        return list(self.providers)


@lru_cache
def get_oidc_settings() -> OpenIdConnectSettings:
    return OpenIdConnectSettings()
```

Environment layout (single provider today, add a sibling block per provider
later — no code change):

```bash
# .secrets.env / compose
OIDC__PROVIDERS__KEYCLOAK__ISSUER=https://localhost:8443/realms/fmv
OIDC__PROVIDERS__KEYCLOAK__AUDIENCE=fmv-demo-api
OIDC__PROVIDERS__KEYCLOAK__CLIENT_ID=fmv-web
OIDC__PROVIDERS__KEYCLOAK__ROLE_CLAIMS=groups
OIDC__PROVIDERS__KEYCLOAK__VERIFY_SSL=false   # dev only
OIDC__DEFAULT_PROVIDER=keycloak
SESSION_SECRET_KEY=<generated>
```

Notes:
- `signing_key_id` is deleted (defect 2). This is a breaking *config* change;
  acceptable because auth was never active.
- `@lru_cache` factories replace module-level singletons everywhere in
  `config/*` so imports do not require secrets (testability).

### 4.2 Token validation flow

1. Extract bearer token (`HTTPBearer`).
2. Read `iss` from the **unverified** payload. This value is used only to
   *route* to the right provider — it is not trusted. The final `decode`
   still enforces `iss` against the matched provider.
3. Look up the provider by `iss` in `providers`. Unknown issuer → 401.
4. Validate with that provider's cached `PyJWKClient` via
   `get_signing_key_from_jwt` (header `kid`, rotation-safe), audience,
   `RS256`, exp/iat/nbf.
5. Return the **payload** dict (fixes defect 1).
6. `validate_scope` matches required scopes against the provider's
   `role_claims` list (contract per D3).

Clients are built once in lifespan and stored on `app.state.oidc_clients:
dict[str, PyJWKClient]`; dependencies read from there.

### 4.3 Session exchange contract (recommended D1=a)

```
Browser                    API
  |-- POST /auth/login ---->   Authorization: Bearer <id_token from IdP>
  |                            validate token (4.2)
  |                            upsert user; reject if user.active is False
  |                            session["user"] = {...}; rotate session
  |<-- Set-Cookie: session=... HttpOnly Secure SameSite=strict
  |-- GET /robots ---------->   cookie only; no bearer needed
  |<-- 200 / 401
```

- `/auth/login` is the only bearer-consuming route for browsers.
- Protected routes use a `get_current_user` dependency that reads the session
  (UI) or a validated bearer (machine clients, later).
- `rotate_session` becomes: clear + repopulate `request.session`; delete the
  manual cookie code.

### 4.4 Frontend

- Add `oidc-client-ts` to `ui/package.json`.
- Create `ui/src/composables/auth.ts` exporting `useUserManager()` backed by
  `UserManager` (settings from `VITE_OIDC_*` env). This restores the missing
  file the existing components already call.
- Flow: `LoginForm.vue` → `signinRedirect()`; `callback.vue` →
  `signinRedirectCallback()` then `POST /auth/login` with the access/id token;
  `logout.vue` → `POST /auth/logout` + `signoutRedirect()`.
- `ui/src/lib/index.ts`: add `credentials: 'include'` to the openapi-fetch
  client.
- `CORS_ALLOW_CREDENTIALS=true` in `.mise.toml` with explicit origins
  (wildcard origins with credentials is invalid CORS).
- Multi-provider later: provider list + picker in login UI; backend already
  supports it.

### 4.5 Compose / CI wiring

Add to `api` service (and `workers` if they validate tokens) in
`docker-compose.yaml`:

```yaml
    environment:
      - SESSION_SECRET_KEY=${SESSION_SECRET_KEY:?Variable not set}
      - OIDC__PROVIDERS__KEYCLOAK__ISSUER=${OIDC__PROVIDERS__KEYCLOAK__ISSUER:?Variable not set}
      - OIDC__PROVIDERS__KEYCLOAK__AUDIENCE=${OIDC__PROVIDERS__KEYCLOAK__AUDIENCE:?Variable not set}
      - CORS_ALLOW_CREDENTIALS=true
```

Without this the container crashes at import with a pydantic `ValidationError`
(verified: these fields are required today and compose injects only declared
variables).

## 5. Known limitations

- No token revocation path before expiry (introspection deferred, D2).
- No refresh-token flow in the session model; session cookie max_age governs.
- Frontend multi-provider UI not built; backend is multi-provider-ready.
- e2e blocked until D6 (dev IdP) is chosen and wired.

## 6. Implementation phases

- [ ] **Phase 0** — Owner answers D1–D7. Record in `decisions-log.md`.
- [ ] **Phase 1** — Config: multi-provider model, `@lru_cache` factories,
      conftest defaults. Update `.mise.toml` / `.secrets.env.example`.
- [ ] **Phase 2** — Backend validation: payload-shape fix, per-provider cached
      JWKS clients, header `kid`, `verify_ssl` flag, provider routing by `iss`.
- [ ] **Phase 3** — Session exchange: fix `login_session` (active check,
      defensive claim mapping), fix `rotate_session`, `get_current_user`
      dependency, protect robot router, scope constants.
- [ ] **Phase 4** — Frontend: `oidc-client-ts` dep, restore `auth.ts`
      composable, `credentials: 'include'`, CORS credentials.
- [ ] **Phase 5** — Infra: compose env vars, dev IdP per D6, e2e happy path.
- [ ] **Phase 6** — Docs: README auth section, `.env` documentation,
      decisions-log entry.

## 7. Test plan

- Unit (`src/`): config parses multi-provider env; provider lookup by `iss`;
  unknown issuer → 401; payload-shape regression; scope allow/deny; inactive
  user login rejected; missing-claims login does not 500.
- Endpoint (`src/api/v1`): 401 without token/cookie; 403 wrong scope; 200 with
  valid session. Use a fake JWKS (cassette or in-process key set) — no live
  IdP in unit tests.
- Frontend (Vitest): `useUserManager` settings assembly; callback posts token
  to `/auth/login`.
- E2E (WDIO): login redirect → callback → protected page renders → logout.
- Gate: `just analyze` and `just e2e` green on a clean clone with
  `.secrets.env` populated.

## 8. Security requirements (from `security-patterns.md`)

- Secrets only via env; never logged. `SESSION_SECRET_KEY` generated, not
  committed.
- TLS to IdP on by default (D7); dev opt-out flagged in docs.
- Least privilege scopes per endpoint; deny by default.
- Validate all claims at the boundary; fail closed.

## 9. References

- `docs/` — this plan lives here; keep updated per documentation standards.
- `.opencode/context/project-intelligence/decisions-log.md` — record D1–D7.
- `.opencode/context/development/principles/api-design.md` — 401/403 semantics.
- Existing code: `src/api/v1/dependencies/auth.py`, `src/api/v1/endpoints/auth.py`.
