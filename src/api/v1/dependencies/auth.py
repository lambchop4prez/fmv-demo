"""OIDC bearer token validation dependencies.

Implements the token validation flow of ``docs/oidc-plan.md`` section 4.2
and fixes the original defects 1-4:

1. ``validate_token`` returns the decoded *payload* dict, not the
   ``jwt.decode_complete`` envelope (``{"header", "payload", "signature"}``).
2. Signing keys are selected by the token header ``kid`` (rotation-safe),
   never by a static configured key id; an unknown ``kid`` yields HTTP 401
   instead of a ``KeyError`` escaping as a 500.
3. ``jwt.PyJWKClient`` instances are built once per provider in the
   application lifespan and stored on ``app.state.oidc_clients``
   (``build_oidc_clients``), never constructed per request.
4. TLS verification to IdP JWKS endpoints is on by default; a provider
   opts out only with ``verify_ssl: false`` (dev/self-signed only).

Provider routing reads ``iss`` from the *unverified* payload purely to
select provider configuration; the final ``jwt.decode`` re-enforces ``iss``
(plus audience, timestamps and signature) against the matched provider, so
the routing read cannot be abused.

Status-code semantics (RFC 9110): every authentication failure yields HTTP
401; an authenticated caller with insufficient scopes yields HTTP 403.
"""

import ssl
from typing import Annotated, Any

import jwt
from config.oidc import OidcProviderSettings, get_oidc_settings
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)

# auto_error=False so missing/invalid credentials are handled here as 401;
# HTTPBearer's default raises 403, which is wrong for unauthenticated.
bearer = HTTPBearer(auto_error=False)

# Static JWKS keysets parsed once per provider name and reused. Static
# keysets are immutable configuration, so per-request parsing is overhead.
_static_keysets: dict[str, jwt.PyJWKSet] = {}


def _unauthorized(detail: str = "Could not validate credentials") -> HTTPException:
    """Build the standard 401 for any authentication failure."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def route_provider_by_iss(iss: object) -> tuple[str, OidcProviderSettings]:
    """Match a configured provider by its ``issuer``.

    ``iss`` is read from an *unverified* token payload and is used only to
    route to provider configuration; the final decode still enforces ``iss``
    against the matched provider. Unknown or missing issuer fails closed
    with HTTP 401.
    """
    if isinstance(iss, str):
        for name, provider in get_oidc_settings().providers.items():
            if provider.issuer == iss:
                return name, provider
    raise _unauthorized("Unknown token issuer")


def _is_static_provider(provider: OidcProviderSettings) -> bool:
    """True when the provider validates against a static JWKS stub."""
    return provider.static_jwks is not None or provider.static_jwks_file is not None


def build_ssl_context(provider: OidcProviderSettings) -> ssl.SSLContext:
    """TLS context for a provider's JWKS fetch.

    Verification stays on (hostname check + certificate validation) unless
    the provider explicitly opts out via ``verify_ssl: false``, which is
    intended for dev/self-signed IdPs only.
    """
    context = ssl.create_default_context()  # check_hostname + CERT_REQUIRED
    if not provider.verify_ssl:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def build_oidc_clients() -> dict[str, jwt.PyJWKClient]:
    """Build one cached ``PyJWKClient`` per network-backed provider.

    Called once from the application lifespan. Providers configured with
    ``static_jwks`` / ``static_jwks_file`` (the dev/CI static-key stub)
    get no client: they never touch the network.
    """
    clients: dict[str, jwt.PyJWKClient] = {}
    for name, provider in get_oidc_settings().providers.items():
        if _is_static_provider(provider):
            continue
        clients[name] = jwt.PyJWKClient(
            provider.jwks_url,
            ssl_context=build_ssl_context(provider),
            cache_keys=True,
            lifespan=provider.jwks_cache_seconds,
        )
    return clients


def _static_keyset(provider_name: str, provider: OidcProviderSettings) -> jwt.PyJWKSet:
    """Parse (once) the static JWKS for a provider into a key set."""
    keyset = _static_keysets.get(provider_name)
    if keyset is None:
        if provider.static_jwks is not None:
            keyset = jwt.PyJWKSet.from_dict(provider.static_jwks)
        elif provider.static_jwks_file is not None:
            keyset = jwt.PyJWKSet.from_json(
                provider.static_jwks_file.read_text(encoding="utf-8")
            )
        else:
            # Guarded by resolve_signing_key; fail closed if reached.
            raise _unauthorized()
        _static_keysets[provider_name] = keyset
    return keyset


def resolve_signing_key(
    provider_name: str,
    provider: OidcProviderSettings,
    token: str,
    clients: dict[str, jwt.PyJWKClient],
) -> jwt.PyJWK:
    """Resolve the signing key for ``token`` by its header ``kid``.

    Static-key providers resolve offline from their static JWKS. All other
    providers use the cached ``PyJWKClient`` built once in the lifespan.
    Unknown ``kid`` or missing client fails closed with HTTP 401.
    """
    if _is_static_provider(provider):
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not isinstance(kid, str):
            raise _unauthorized("Token header is missing a key id (kid)")
        keyset = _static_keyset(provider_name, provider)
        key = jwt.PyJWKClient.match_kid(keyset.keys, kid)
        if key is None:
            raise _unauthorized("Unknown token signing key")
        return key

    client = clients.get(provider_name)
    if client is None:
        # Lifespan did not run or provider misconfigured: fail closed.
        raise _unauthorized("No JWKS client configured for provider")
    return client.get_signing_key_from_jwt(token)


async def validate_token(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict[str, Any]:
    """Validate the bearer token and return the decoded **payload** dict."""
    if credentials is None:
        raise _unauthorized("Invalid authorization token")
    token = credentials.credentials

    # Routing read: unverified, used only to pick the provider config.
    try:
        unverified: dict[str, Any] = jwt.decode(
            token, options={"verify_signature": False}
        )
    except jwt.PyJWTError:
        raise _unauthorized("Invalid authorization token") from None

    provider_name, provider = route_provider_by_iss(unverified.get("iss"))

    # Mirrored onto the mounted v1 app in the lifespan (see main.py).
    clients: dict[str, jwt.PyJWKClient] = getattr(request.app.state, "oidc_clients", {})

    try:
        signing_key = resolve_signing_key(provider_name, provider, token, clients)
        # Key is selected by the token header 'kid' (static keyset or the
        # provider's cached client), surviving IdP key rotation. Passing the
        # PyJWK binds verification to the key's own algorithm as well.
        payload: dict[str, Any] = jwt.decode(
            jwt=token,
            key=signing_key,
            algorithms=["RS256"],
            audience=provider.audience,
            issuer=provider.issuer,
            options={
                # "strict_aud": True,
                "enforce_minimum_key_length": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_jti": True,
                "verify_nbf": True,
                "verify_signature": True,
                "verify_sub": True,
            },
        )
    except jwt.PyJWTError:
        # Covers InvalidTokenError and key-resolution failures
        # (PyJWKClientError / PyJWKSetError): 401, never a 500.
        raise _unauthorized("Invalid authorization token") from None

    return payload


async def validate_scope(
    security_scopes: SecurityScopes,
    token: Annotated[dict[str, Any], Depends(validate_token)],
) -> None:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    if not security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # The payload was validated by validate_token; route again by its now
    # verified 'iss' to find this provider's role claim name.
    _, provider = route_provider_by_iss(token.get("iss"))
    scopes = token.get(provider.role_claims)
    if isinstance(scopes, str):
        # Some IdPs deliver role/scope claims as space-delimited strings.
        scopes = scopes.split()
    required = set(security_scopes.scopes)
    if not isinstance(scopes, list) or not required.issubset(scopes):
        # Authenticated but insufficient privileges: 403 per RFC 9110.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )
