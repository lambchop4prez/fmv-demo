#!/usr/bin/env bash
# TEST KEY ONLY, NEVER PRODUCTION.
#
# Generates (or regenerates) the dev/e2e OIDC test keypair fixtures used by
# the static-key stub (decision D2/D6):
#
#   src/test/fixtures/oidc_test_private_key.pem  (TEST signing key, mock IdP)
#   src/test/fixtures/oidc_test_jwks.json        (public JWKS, api + mock IdP)
#
# Usage (from anywhere):
#   bash ci/fixtures/generate-test-keypair.sh
#
# After regenerating, restart api and mock-idp so both reload the keys:
#   docker compose --profile backend restart api workers mock-idp
#
# The script verifies a sign/verify roundtrip before it succeeds, so a
# corrupted PEM header or a mismatched JWKS fails loudly here, not later.
set -euo pipefail

KID="fmv-test-key-1"
FIXTURES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../src/test/fixtures" && pwd)"

# Keep umask strict: even test keys should not be world-writable by habit.
umask 077

mkdir -p "$FIXTURES_DIR"
cd "$FIXTURES_DIR"

# 1. RSA 2048 private key in PKCS#8 PEM.
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out oidc_test_private_key.pem.tmp

# 2. Loud test-only header above the PEM block. OpenSSL/Node/cryptography all
#    skip leading text before "-----BEGIN", and step 4 proves it round-trips.
cat > oidc_test_private_key.pem <<'EOF'
# =============================================================================
# TEST KEY ONLY, NEVER PRODUCTION
# Throwaway RSA 2048 test keypair for the fmv-demo OIDC dev/CI static-key
# stub (kid: fmv-test-key-1). The matching public JWKS is committed next to
# this file as oidc_test_jwks.json. NEVER use this key outside local dev/e2e.
# =============================================================================
EOF
cat oidc_test_private_key.pem.tmp >> oidc_test_private_key.pem
rm oidc_test_private_key.pem.tmp

# 3. Derive the public JWKS (n/e are base64url straight from node's JWK
#    export) and 4. verify the sign/verify roundtrip through BOTH the
#    commented PEM and the JWKS-derived public key.
KID="$KID" node <<'EOF'
const fs = require("node:fs");
const crypto = require("node:crypto");

const kid = process.env.KID;
const pem = fs.readFileSync("oidc_test_private_key.pem");
const key = crypto.createPrivateKey(pem); // proves the header comment parses
if (key.asymmetricKeyDetails.modulusLength !== 2048) {
  throw new Error("expected RSA 2048 key");
}
const jwk = crypto.createPublicKey(key).export({ format: "jwk" });
const jwks = {
  keys: [{ kty: "RSA", use: "sig", alg: "RS256", kid, n: jwk.n, e: jwk.e }],
};
fs.writeFileSync("oidc_test_jwks.json", JSON.stringify(jwks, null, 2) + "\n");

// Roundtrip: sign with the private key, verify with the public key derived
// from the committed JWKS — proves fixture consistency before commit.
const pubFromJwks = crypto.createPublicKey({ key: jwks.keys[0], format: "jwk" });
const data = Buffer.from("fmv-test-roundtrip");
const signature = crypto.sign("sha256", data, key);
if (!crypto.verify("sha256", data, pubFromJwks, signature)) {
  throw new Error("sign/verify roundtrip failed");
}
console.log(`OK: keypair + JWKS verified (kid=${kid})`);
EOF

chmod 600 oidc_test_private_key.pem
shasum -a 256 oidc_test_private_key.pem oidc_test_jwks.json
