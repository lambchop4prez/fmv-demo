"""Unit tests for the OIDC auth dependencies (plan section 7, unit).

Covers: provider routing by ``iss`` (401 fail-closed), the payload-shape
regression guard against the old ``decode_complete`` envelope bug (defect
1), key resolution by header ``kid`` from the static JWKS (defect 2, no
network), TLS context defaults (defect 4), and scope allow/deny (403).
"""

import ssl
import time
from collections.abc import Mapping
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes

from api.v1.dependencies.auth import (
    build_oidc_clients,
    build_ssl_context,
    resolve_signing_key,
    route_provider_by_iss,
    validate_scope,
    validate_token,
)

TEST_ISSUER = "https://oidc.test/realms/fmv"
TEST_AUDIENCE = "fmv-demo-api"
TEST_KID = "fmv-test-key-1"


@pytest.fixture
def app() -> FastAPI:
    """Bare app for ``Request`` scopes (state.oidc_clients stays absent).

    Static-JWKS providers never consult ``app.state.oidc_clients``, so a
    bare app is enough and no lifespan/network code runs.
    """
    return FastAPI()


@pytest.fixture
def make_request(app: FastAPI) -> Any:
    """Build a minimal ``Request`` with optional headers."""

    def build(headers: Mapping[str, str] | None = None) -> Request:
        scope: dict[str, Any] = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [
                (key.lower().encode(), value.encode())
                for key, value in (headers or {}).items()
            ],
            "query_string": b"",
            "app": app,
        }
        return Request(scope)

    return build


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


# --- provider routing by iss -------------------------------------------------
def test_route_provider_by_iss_returns_match() -> None:
    name, provider = route_provider_by_iss(TEST_ISSUER)
    assert name == "test"
    assert provider.issuer == TEST_ISSUER
    assert provider.audience == TEST_AUDIENCE


def test_route_provider_by_iss_unknown_issuer_yields_401() -> None:
    with pytest.raises(HTTPException) as excinfo:
        route_provider_by_iss("https://evil.test/realms/x")
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_route_provider_by_iss_non_string_yields_401() -> None:
    with pytest.raises(HTTPException) as excinfo:
        route_provider_by_iss(None)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


# --- validate_token: payload shape + accept/reject --------------------------
@pytest.mark.anyio
async def test_validate_token_returns_payload_not_envelope(
    make_request: Any, id_token_factory: Any
) -> None:
    """Regression guard (defect 1): payload dict, not decode_complete."""
    token = id_token_factory(sub="payload-shape-user", scopes=["robot:read"])
    request = make_request({"authorization": f"Bearer {token}"})
    payload = await validate_token(request, _credentials(token))

    assert isinstance(payload, dict)
    assert payload["sub"] == "payload-shape-user"
    assert payload["iss"] == TEST_ISSUER
    # The old defect returned {"header": ..., "payload": ..., "signature": ...}
    assert "payload" not in payload
    assert "header" not in payload
    assert "signature" not in payload


@pytest.mark.anyio
async def test_validate_token_valid_token_yields_payload(
    make_request: Any, id_token_factory: Any
) -> None:
    token = id_token_factory(sub="u-valid", scopes=["robot:read", "robot:run"])
    request = make_request({"authorization": f"Bearer {token}"})
    payload = await validate_token(request, _credentials(token))

    assert payload["sub"] == "u-valid"
    assert payload["aud"] == TEST_AUDIENCE
    assert payload["groups"] == ["robot:read", "robot:run"]


@pytest.mark.anyio
async def test_validate_token_expired_yields_401(
    make_request: Any, id_token_factory: Any
) -> None:
    token = id_token_factory(sub="u-expired", expires_in=-60)
    request = make_request({"authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as excinfo:
        await validate_token(request, _credentials(token))
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_validate_token_garbage_yields_401(make_request: Any) -> None:
    garbage = "garbage.not.jwt"
    request = make_request({"authorization": f"Bearer {garbage}"})
    with pytest.raises(HTTPException) as excinfo:
        await validate_token(request, _credentials(garbage))
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_validate_token_missing_credentials_yields_401(
    make_request: Any,
) -> None:
    # HTTPBearer(auto_error=False) hands us None: the dep must 401 itself.
    with pytest.raises(HTTPException) as excinfo:
        await validate_token(make_request(), None)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_validate_token_wrong_audience_yields_401(
    make_request: Any, id_token_factory: Any
) -> None:
    token = id_token_factory(sub="u-aud", audience="someone-elses-api")
    request = make_request({"authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as excinfo:
        await validate_token(request, _credentials(token))
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_validate_token_forged_signature_yields_401(
    make_request: Any,
) -> None:
    """Token with valid claims but signed by a foreign key fails closed."""
    foreign_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issued_at = int(time.time())
    forged = jwt.encode(
        {
            "iss": TEST_ISSUER,
            "aud": TEST_AUDIENCE,
            "sub": "attacker",
            "iat": issued_at,
            "nbf": issued_at,
            "exp": issued_at + 3600,
            "jti": "forged-jti",
        },
        foreign_key,
        algorithm="RS256",
        headers={"kid": TEST_KID},
    )
    request = make_request({"authorization": f"Bearer {forged}"})
    with pytest.raises(HTTPException) as excinfo:
        await validate_token(request, _credentials(forged))
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


# --- signing key resolution (defect 2) ----------------------------------------
def test_resolve_signing_key_static_by_kid_offline(id_token_factory: Any) -> None:
    from config.oidc import get_oidc_settings

    token = id_token_factory()
    provider = get_oidc_settings().providers["test"]
    # Empty clients dict proves the static path needs no JWKS client.
    key = resolve_signing_key("test", provider, token, clients={})
    assert key.key_id == TEST_KID


def test_resolve_signing_key_unknown_kid_yields_401(id_token_factory: Any) -> None:
    from config.oidc import get_oidc_settings

    token = id_token_factory(kid="rotated-key-999")
    provider = get_oidc_settings().providers["test"]
    with pytest.raises(HTTPException) as excinfo:
        resolve_signing_key("test", provider, token, clients={})
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_resolve_signing_key_missing_kid_yields_401(id_token_factory: Any) -> None:
    from config.oidc import get_oidc_settings

    token = id_token_factory(include_kid=False)
    provider = get_oidc_settings().providers["test"]
    with pytest.raises(HTTPException) as excinfo:
        resolve_signing_key("test", provider, token, clients={})
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


# --- JWKS clients + TLS (defects 3 and 4) ------------------------------------
def test_build_oidc_clients_skips_static_providers() -> None:
    """Static-key providers never touch the network: no client built (D2)."""
    clients = build_oidc_clients()
    assert "test" not in clients


def test_build_oidc_clients_network_provider_verifies_tls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Network-backed providers get one cached client, TLS on by default."""
    from config.oidc import get_oidc_settings

    monkeypatch.setenv("OIDC__PROVIDERS__NETPROV__ISSUER", "https://net.test")
    monkeypatch.setenv("OIDC__PROVIDERS__NETPROV__AUDIENCE", "net-api")
    get_oidc_settings.cache_clear()
    try:
        clients = build_oidc_clients()
        assert "netprov" in clients
        context = clients["netprov"].ssl_context
        assert context is not None
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname is True
    finally:
        get_oidc_settings.cache_clear()


def test_build_ssl_context_verify_ssl_opt_out() -> None:
    """Dev-only opt-out flips to CERT_NONE; the default stays strict (D7)."""
    from config.oidc import OidcProviderSettings

    strict = build_ssl_context(
        OidcProviderSettings(issuer="https://net.test", audience="net-api")
    )
    assert strict.verify_mode == ssl.CERT_REQUIRED
    assert strict.check_hostname is True

    lenient = build_ssl_context(
        OidcProviderSettings(
            issuer="https://net.test", audience="net-api", verify_ssl=False
        )
    )
    assert lenient.verify_mode == ssl.CERT_NONE


# --- validate_scope (403 semantics) -------------------------------------------
@pytest.mark.anyio
async def test_validate_scope_allowed() -> None:
    payload: dict[str, Any] = {"iss": TEST_ISSUER, "groups": ["robot:read"]}
    # Returns None on success; a non-raise is the assertion.
    await validate_scope(SecurityScopes(scopes=["robot:read"]), payload)


@pytest.mark.anyio
async def test_validate_scope_missing_scope_yields_403() -> None:
    payload: dict[str, Any] = {"iss": TEST_ISSUER, "groups": ["robot:read"]}
    with pytest.raises(HTTPException) as excinfo:
        await validate_scope(SecurityScopes(scopes=["robot:write"]), payload)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_validate_scope_space_delimited_claim_supported() -> None:
    """Some IdPs deliver role claims as space-delimited strings."""
    payload: dict[str, Any] = {
        "iss": TEST_ISSUER,
        "groups": "robot:read robot:run",
    }
    # Returns None on success; a non-raise is the assertion.
    await validate_scope(SecurityScopes(scopes=["robot:run"]), payload)

    with pytest.raises(HTTPException) as excinfo:
        await validate_scope(SecurityScopes(scopes=["robot:write"]), payload)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_validate_scope_malformed_claim_denies_by_default() -> None:
    payload: dict[str, Any] = {"iss": TEST_ISSUER, "groups": 42}
    with pytest.raises(HTTPException) as excinfo:
        await validate_scope(SecurityScopes(scopes=["robot:read"]), payload)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
