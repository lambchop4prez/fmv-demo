"""Mock OIDC identity provider for local dev and e2e ONLY. NEVER deploy.

Implements the minimal authorization-code flow (PKCE-tolerant) that
oidc-client-ts drives with response_type=code:

    GET  {issuer}/.well-known/openid-configuration   discovery document
    GET  {issuer}/.well-known/jwks.json              static public JWKS fixture
    GET  {issuer}/authorize                           minimal login form
    POST {issuer}/authorize                           accepts ANY credentials,
                                                      issues a single-use code,
                                                      302 back to redirect_uri
    POST {issuer}/token                               code -> RS256-signed tokens
    GET  {issuer}/logout                              redirects post-logout

The api service never talks to this container: it verifies tokens offline
against the same public JWKS fixture (static-key stub, decision D6). The
mock exists only to complete the browser redirect flow for the frontend.

id_tokens carry aud=[AUDIENCE, CLIENT_ID] so the same token passes both the
backend check (audience "fmv-demo-api") and oidc-client-ts (aud contains the
client_id). Any username/password is accepted; identity claims derive from
the username.

TEST ONLY, NEVER PRODUCTION.
"""

from __future__ import annotations

import base64
import hashlib
import html
import ipaddress
import json
import logging
import os
import secrets
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import jwt
import uvicorn
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import NameOID
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

logging.basicConfig(level=logging.INFO, format="[mock-idp] %(levelname)s %(message)s")
log = logging.getLogger("mock-idp")

ISSUER = os.environ.get("MOCK_IDP_ISSUER", "https://localhost:8443/realms/fmv").rstrip(
    "/"
)
CLIENT_ID = os.environ.get("MOCK_IDP_CLIENT_ID", "fmv-web")
AUDIENCE = os.environ.get("MOCK_IDP_AUDIENCE", "fmv-demo-api")
KID = os.environ.get("MOCK_IDP_KID", "fmv-test-key-1")
GROUPS = [
    g
    for g in os.environ.get(
        "MOCK_IDP_GROUPS", "robot:read,robot:write,robot:run,user,admin"
    ).split(",")
    if g
]
TOKEN_TTL_SECONDS = int(os.environ.get("MOCK_IDP_TOKEN_TTL", "300"))
CODE_TTL_SECONDS = 60
PREFIX = urlsplit(ISSUER).path.rstrip("/")
PRIVATE_KEY_FILE = Path(
    os.environ.get("MOCK_IDP_PRIVATE_KEY_FILE", "/fixtures/oidc_test_private_key.pem")
)
JWKS_FILE = Path(os.environ.get("MOCK_IDP_JWKS_FILE", "/fixtures/oidc_test_jwks.json"))
TLS_MOUNT_DIR = Path(os.environ.get("MOCK_IDP_TLS_MOUNT", "/certs"))
TLS_FALLBACK_DIR = Path(os.environ.get("MOCK_IDP_TLS_FALLBACK", "/run/mock-idp-certs"))
# Offline-safe placeholder avatar: inline SVG data URI, no external fetch.
PICTURE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' fill='%234f46e5'/%3E"
    "%3Ctext x='32' y='40' font-size='28' text-anchor='middle' fill='white'%3EM%3C/text%3E%3C/svg%3E"
)

# In-memory single-use authorization codes. A restart wipes them; codes live
# for seconds, which is fine for a dev/e2e mock.
_codes: dict[str, dict[str, str | float]] = {}


def _startup_checks() -> str:
    """Fail fast when fixtures are missing or inconsistent. Loud by design."""
    log.warning("TEST ONLY mock IdP — issuer=%s — NEVER PRODUCTION", ISSUER)
    raw = PRIVATE_KEY_FILE.read_text(encoding="utf-8")
    start = raw.find("-----BEGIN")
    if start < 0:
        raise RuntimeError(f"{PRIVATE_KEY_FILE} does not contain a PEM block")
    private_pem = raw[start:]
    priv = load_pem_private_key(private_pem.encode(), password=None)
    jwks_text = JWKS_FILE.read_text(encoding="utf-8")
    matched = [k for k in jwt.PyJWKSet.from_json(jwks_text).keys if k.key_id == KID]
    if not matched:
        raise RuntimeError(f"{JWKS_FILE} contains no key with kid '{KID}'")
    if matched[0].key.public_numbers().n != priv.public_key().public_numbers().n:
        raise RuntimeError("private key fixture does not match the public JWKS fixture")
    return private_pem


PRIVATE_PEM = _startup_checks()

app = FastAPI(title="fmv-demo mock IdP (TEST ONLY)", docs_url=None, redoc_url=None)

# The frontend calls POST {issuer}/token cross-origin from the app origin.
# Without CORS the browser blocks it and signinCallback() fails. No cookies
# are sent to the IdP, so credentials are not enabled here.
CORS_ORIGINS = [
    o
    for o in os.environ.get(
        "MOCK_IDP_CORS_ORIGINS",
        "http://localhost:8080,https://localhost:5173,https://localhost:8800",
    ).split(",")
    if o
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def _form_html(params: dict[str, str]) -> str:
    """Login form re-submitting every original /authorize param unchanged."""
    hidden = "\n".join(
        f'<input type="hidden" name="{html.escape(k, quote=True)}" value="{html.escape(v, quote=True)}" />'
        for k, v in params.items()
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>mock IdP — TEST ONLY</title>
<style>body{{font-family:system-ui;display:grid;place-items:center;min-height:100vh;margin:0;background:#111827;color:#e5e7eb}}
main{{background:#1f2937;padding:2rem;border-radius:.5rem;width:20rem}}
h1{{font-size:1.1rem;margin:0 0 .25rem}}p.warn{{color:#f87171;font-size:.75rem;margin:0 0 1rem}}
label{{display:block;margin:.75rem 0 .25rem;font-size:.85rem}}
input{{width:100%;padding:.5rem;border-radius:.25rem;border:1px solid #4b5563;background:#111827;color:#e5e7eb;box-sizing:border-box}}
button{{margin-top:1rem;width:100%;padding:.5rem;border:0;border-radius:.25rem;background:#4f46e5;color:white;font-weight:600;cursor:pointer}}</style>
</head><body><main>
<h1>fmv-demo mock IdP</h1>
<p class="warn">TEST ONLY — accepts any username and password.</p>
<form method="post" action="{html.escape(PREFIX + "/authorize", quote=True)}">
{hidden}
<label for="username">Username</label>
<input id="username" name="username" value="demo" required autofocus />
<label for="password">Password</label>
<input id="password" name="password" type="password" value="demo" required />
<button type="submit">Sign in</button>
</form></main></body></html>"""


def _valid_redirect(uri: str) -> bool:
    """Dev-only guard: loopback redirect targets, prevents open redirects."""
    parts = urlsplit(uri)
    return parts.scheme in {"http", "https"} and parts.hostname in {
        "localhost",
        "127.0.0.1",
    }


def _token_error(error: str) -> JSONResponse:
    return JSONResponse(
        {"error": error}, status_code=400, headers={"Cache-Control": "no-store"}
    )


def _prune_codes() -> None:
    now = time.time()
    for stale in [c for c, e in _codes.items() if float(e["expires_at"]) < now]:
        _codes.pop(stale, None)


def _pkce_ok(verifier: str, challenge: str, method: str) -> bool:
    if not verifier:
        return False
    if method == "S256":
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return (
            base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii") == challenge
        )
    return verifier == challenge  # "plain"


def _sign(claims: dict[str, object]) -> str:
    return jwt.encode(claims, PRIVATE_PEM, algorithm="RS256", headers={"kid": KID})


@app.get("/")
def index() -> JSONResponse:
    """Human pointer to the moving parts; not part of the OIDC contract."""
    return JSONResponse(
        {
            "name": "fmv-demo mock IdP",
            "test_only": True,
            "discovery": f"{PREFIX}/.well-known/openid-configuration",
        }
    )


@app.get(f"{PREFIX}/.well-known/openid-configuration")
def openid_configuration() -> JSONResponse:
    return JSONResponse(
        {
            "issuer": ISSUER,
            "authorization_endpoint": f"{ISSUER}/authorize",
            "token_endpoint": f"{ISSUER}/token",
            "jwks_uri": f"{ISSUER}/.well-known/jwks.json",
            "response_types_supported": ["code"],
            "response_modes_supported": ["query"],
            "grant_types_supported": ["authorization_code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email"],
            "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
            "code_challenge_methods_supported": ["S256", "plain"],
        }
    )


@app.get(f"{PREFIX}/.well-known/jwks.json")
@app.get(f"{PREFIX}/jwks")
def jwks() -> JSONResponse:
    """Same static public JWKS the api mounts for offline verification."""
    return JSONResponse(json.loads(JWKS_FILE.read_text(encoding="utf-8")))


@app.get(f"{PREFIX}/authorize", response_class=HTMLResponse)
def authorize_form(request: Request) -> str:
    params = dict(request.query_params)  # last value wins per repeated key
    if not params.get("redirect_uri"):
        raise HTTPException(status_code=400, detail="redirect_uri is required")
    if not _valid_redirect(params["redirect_uri"]):
        raise HTTPException(
            status_code=400, detail="redirect_uri must be loopback (dev mock)"
        )
    return _form_html(params)


@app.post(f"{PREFIX}/authorize")
async def authorize_submit(request: Request) -> RedirectResponse:
    """Accept ANY credentials (mock), mint a single-use code, redirect back."""
    fields = {k: str(v) for k, v in (await request.form()).items()}
    username = fields.get("username", "").strip()
    redirect_uri = fields.get("redirect_uri", "")
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    if not _valid_redirect(redirect_uri):
        raise HTTPException(
            status_code=400, detail="redirect_uri must be loopback (dev mock)"
        )
    _prune_codes()
    code = secrets.token_urlsafe(24)
    _codes[code] = {
        "sub": username,
        "redirect_uri": redirect_uri,
        "client_id": fields.get("client_id", CLIENT_ID),
        "nonce": fields.get("nonce", ""),
        "scope": fields.get("scope", "openid profile email"),
        "code_challenge": fields.get("code_challenge", ""),
        "code_challenge_method": fields.get("code_challenge_method", ""),
        "expires_at": time.time() + CODE_TTL_SECONDS,
    }
    query = {"code": code}
    if fields.get("state"):
        query["state"] = fields["state"]
    log.info("issued code for sub=%s", username)
    return RedirectResponse(f"{redirect_uri}?{urlencode(query)}", status_code=302)


@app.post(f"{PREFIX}/token")
async def token_exchange(request: Request) -> JSONResponse:
    """Exchange a single-use code for RS256-signed dev tokens."""
    fields = {k: str(v) for k, v in (await request.form()).items()}
    if fields.get("grant_type") != "authorization_code":
        return _token_error("unsupported_grant_type")
    entry = _codes.pop(fields.get("code", ""), None)
    if entry is None or float(entry["expires_at"]) < time.time():
        return _token_error("invalid_grant")
    if fields.get("redirect_uri", "") != entry["redirect_uri"]:
        return _token_error("invalid_grant")
    if fields.get("client_id", CLIENT_ID) != entry["client_id"]:
        return _token_error("invalid_grant")
    challenge = str(entry["code_challenge"])
    if challenge and not _pkce_ok(
        fields.get("code_verifier", ""),
        challenge,
        str(entry["code_challenge_method"]) or "plain",
    ):
        return _token_error("invalid_grant")

    now = int(time.time())
    sub = str(entry["sub"])
    base: dict[str, object] = {
        "iss": ISSUER,
        "sub": sub,
        "aud": [AUDIENCE, CLIENT_ID],
        "iat": now,
        "nbf": now,
        "exp": now + TOKEN_TTL_SECONDS,
        "jti": str(uuid.uuid4()),
        "name": sub,
        "preferred_username": sub,
        "email": f"{sub}@example.com",
        "email_verified": True,
        "picture": PICTURE,
        "groups": GROUPS,
    }
    id_claims = dict(base)
    if entry["nonce"]:
        id_claims["nonce"] = entry["nonce"]
    access_claims = dict(base)
    access_claims["scope"] = entry["scope"]
    log.info("issued tokens for sub=%s", sub)
    return JSONResponse(
        {
            "access_token": _sign(access_claims),
            "id_token": _sign(id_claims),
            "token_type": "Bearer",
            "expires_in": TOKEN_TTL_SECONDS,
            "scope": entry["scope"],
        },
        headers={"Cache-Control": "no-store"},
    )


@app.get(f"{PREFIX}/logout")
def logout(post_logout_redirect_uri: str | None = None) -> Response:
    if post_logout_redirect_uri and _valid_redirect(post_logout_redirect_uri):
        return RedirectResponse(post_logout_redirect_uri, status_code=302)
    return HTMLResponse("<h1>mock IdP — signed out (TEST ONLY)</h1>")


def _resolve_tls_paths() -> tuple[str, str]:
    """Prefer mounted mkcert certs from `just setup`; else self-sign locally.

    An ephemeral self-signed cert means e2e browsers must accept insecure
    certs or trust this container's CA; mounted mkcert certs are trusted by
    any machine that ran `just setup`.
    """
    mounted = (TLS_MOUNT_DIR / "cert.pem", TLS_MOUNT_DIR / "key.pem")
    if all(p.is_file() for p in mounted):
        return str(mounted[0]), str(mounted[1])
    TLS_FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
    cert_path, key_path = TLS_FALLBACK_DIR / "cert.pem", TLS_FALLBACK_DIR / "key.pem"
    if not (cert_path.is_file() and key_path.is_file()):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        now = datetime.now(UTC)
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )
        key_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        log.warning(
            "no /certs mount — generated ephemeral self-signed TLS cert; clients need acceptInsecureCerts or mkcert trust"
        )
    return str(cert_path), str(key_path)


if __name__ == "__main__":
    certfile, keyfile = _resolve_tls_paths()
    uvicorn.run(
        app, host="0.0.0.0", port=8443, ssl_certfile=certfile, ssl_keyfile=keyfile
    )
