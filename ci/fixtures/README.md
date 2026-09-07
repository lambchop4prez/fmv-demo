# CI Fixtures — OIDC Test Keypair

:warning: **TEST KEY ONLY, NEVER PRODUCTION.** These fixtures back the
dev/CI static-key stub (decisions D2/D6 in `docs/decisions-log.md`). The
private key is committed on purpose so a clean clone can run e2e without a
live IdP. Never copy it outside this repository's dev/test paths.

## Files

The key material lives in `src/test/fixtures/` (see the deliverable list):

| File | Purpose |
|------|---------|
| `src/test/fixtures/oidc_test_private_key.pem` | TEST RSA 2048 signing key. Used only by the mock IdP (`ci/mock-idp`) to sign dev id_tokens. |
| `src/test/fixtures/oidc_test_jwks.json` | Public JWKS. The api verifies tokens offline against this file via `OIDC__PROVIDERS__KEYCLOAK__STATIC_JWKS_FILE`; the mock IdP serves the same file at its `jwks_uri`. |

`generate-test-keypair.sh` (in this directory) creates both files.

## Generate / regenerate

```bash
bash ci/fixtures/generate-test-keypair.sh
```

The script runs these commands (recorded for auditability):

```bash
# 1. RSA 2048 private key (PKCS#8 PEM), then prepend the loud TEST-ONLY header
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out oidc_test_private_key.pem.tmp

# 2. Derive the public JWKS (n/e base64url) and verify a sign/verify roundtrip
#    with node — see generate-test-keypair.sh for the exact script.
```

After regenerating, restart the containers so both sides reload the keys:

```bash
docker compose --profile backend restart api workers mock-idp
```

## Consistency contract

These values MUST stay identical across all three places; the mock IdP fails
fast at startup if the keypair and JWKS disagree:

| Value | Fixed at | Used by |
|-------|----------|---------|
| `kid` | `fmv-test-key-1` | JWKS fixture, mock IdP `MOCK_IDP_KID`, api key lookup by token header `kid` |
| issuer | `https://localhost:8443/realms/fmv` | `OIDC__PROVIDERS__KEYCLOAK__ISSUER`, `VITE_OIDC_AUTHORITY`, mock IdP `iss` claim |
| audience | `fmv-demo-api` | `OIDC__PROVIDERS__KEYCLOAK__AUDIENCE`, mock IdP `aud` claim |
| client_id | `fmv-web` | `OIDC__PROVIDERS__KEYCLOAK__CLIENT_ID`, `VITE_OIDC_CLIENT_ID`, mock IdP `aud` claim |

The id_token carries `aud=["fmv-demo-api", "fmv-web"]` so the same token
passes the backend audience check and the oidc-client-ts client_id check.

## Fail-closed notes

- `BACKEND_ENVIRONMENT=production` rejects `static_jwks`/`static_jwks_file`
  at api startup.
- The api never fetches the mock IdP's `jwks_uri` in static mode — no
  network path exists between them by design.
- gitleaks may flag `oidc_test_private_key.pem`; this committed test-only key
  is the documented exception. Do not weaken the hook — add a precise
  allowlist entry for this path if the scan blocks commits.
