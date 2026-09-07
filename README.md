# Demo project using FastAPI, MongoDB, and Vue

:construction: :hammer: **Under Construction** :wrench: :construction:

## Tooling

- [`mise`](https://mise.jdx.dev) Manages the dev environment
- [`just`](https://just.systems) Just a task runner
- [Docker](https://www.docker.com/) Containerization platform

To get started, make sure to have `mise` (and docker) installed.

`just` is used as a task runner, you can see the available tasks by running `just --list`

## Development

To get started developing, clone the repo and install dependent tools by running `mise install`.

Setup your environment by running `just setup` and bring up the infrastructure with `just up infra`. Then, 
start up all the dev servers locally with `just dev`. Simple as that.

Additional variations of dev servers can be run via `just backend dev`, `just backend api`, `just backend workers`, and `just ui dev`.

When done, `<Ctrl>c` to stop the dev servers and `just down infra` to teardown the infrastructure.

For more information, see [CONTRIBUTING.md](./CONTRIBUTING.md)

More information can be found in:

  - [Frontend](./ui/README.md)
  - [Backend](./src/README.md)
  - [CONTRIBUTING.md](./CONTRIBUTING.md)

## Authentication

The API uses OpenID Connect (OIDC). The browser logs in through an identity
provider (IdP); the API then keeps the user in a signed session cookie.

How it works:

1. The frontend (`oidc-client-ts`) redirects the browser to the IdP.
2. The IdP sends the browser back to `/callback` with a code.
3. The frontend exchanges the code for an `id_token` and posts it to
   `POST /auth/login` as a bearer token.
4. The API validates the token, stores the user in a session cookie
   (`HttpOnly`, `Secure`, `SameSite=strict`), and returns.
5. All other routes authenticate with the session cookie only. The bearer
   token is used only at `/auth/login`.

Key decisions are recorded in [docs/decisions-log.md](./docs/decisions-log.md).

Configuration:

- Set the variables in `.secrets.env.example` in your `.secrets.env`
  (`SESSION_SECRET_KEY` and the `OIDC__PROVIDERS__<NAME>__*` block).
- Multiple IdPs are supported by adding another `OIDC__PROVIDERS__<NAME>__*`
  block. No code change is required.
- Tokens are verified against the IdP JWKS over TLS by default. Set
  `OIDC__PROVIDERS__<NAME>__VERIFY_SSL=false` only for a self-signed dev IdP.

Local development and CI use a static-key stub plus a tiny mock IdP
(`ci/mock-idp`), so no external IdP is needed:

- The API verifies tokens offline against
  `src/test/fixtures/oidc_test_jwks.json` (set via
  `OIDC__PROVIDERS__<NAME>__STATIC_JWKS_FILE`).
- `ci/mock-idp` signs tokens with the matching test private key and drives
  the browser redirect flow.
- Generate or regenerate the test keypair with
  `bash ci/fixtures/generate-test-keypair.sh`. These keys are for local
  development and tests only. Never use them in production.
- `static_jwks` is rejected at startup when `BACKEND_ENVIRONMENT=production`.

## To Do

- [x] - In memory database stub
- [x] - mongodb database adapter
- [x] - API Authentication (OAuth2/OIDC)
- [x] - Complete docker-compose file
- [x] - Unit/E2E testing

## Reference

- <https://github.com/mongodb-developer/mongodb-pymongo-fastapi>
- <https://github.com/mongodb-labs/full-stack-fastapi-mongodb>
- <https://github.com/antfu-collective/vitesse>
