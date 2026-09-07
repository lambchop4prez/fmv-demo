# Test Fixtures — OIDC Static Keypair (TEST ONLY, NEVER PRODUCTION)

These fixtures back the dev/CI static-key stub (decisions D2/D6). The api
verifies tokens offline against `oidc_test_jwks.json`; the mock IdP
(`ci/mock-idp`) signs dev tokens with `oidc_test_private_key.pem` and serves
the same public JWKS. `kid` is fixed at `fmv-test-key-1` everywhere.

## Status: key material pending generation

The key files are NOT committed yet. The executing agent for subtask
oidc-auth/06 had shell access revoked mid-task (openssl/node blocked), so
key generation — which must be a real computation, never hand-written — was
handed off. Generate them once with:

```bash
bash ci/fixtures/generate-test-keypair.sh
```

The script generates the RSA 2048 keypair with openssl, derives the JWKS
with node, and verifies a sign/verify roundtrip before succeeding. Full
details and the consistency contract: `ci/fixtures/README.md`.

Until the files exist, `just up infra` starts the mock IdP but it exits
immediately with a loud "fixture missing" error (fail closed, by design).
