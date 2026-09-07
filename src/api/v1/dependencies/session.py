"""Session-based authentication dependencies (decision D1=a).

The bearer token is consumed only at ``POST /auth/login``, where the login
exchange stores the identity and scopes in the signed session cookie. Every
other protected route authenticates through that cookie:

- ``get_current_user`` reads ``request.session["user"]`` (HTTP 401 when
  absent, expired, or malformed).
- ``require_scope`` enforces ``request.session["scopes"]`` (HTTP 403 for an
  authenticated caller missing the required scope).

The session cookie is signed by Starlette's ``SessionMiddleware``, so its
contents are trusted once present. Scope constants live in ``api.v1.scopes``
(decision D3); the session scopes are populated at login from the matched
provider's ``role_claims``.

Status-code semantics (RFC 9110): unauthenticated → 401, authenticated but
forbidden → 403.
"""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status


def get_current_user(request: Request) -> dict[str, Any]:
    """Return the user dict stored in the session by the login exchange.

    Raises HTTP 401 when the session carries no user: missing, expired, or
    tampered cookie. No ``WWW-Authenticate`` header: cookie authentication
    is not a challenge scheme.
    """
    user = request.session.get("user")
    if not isinstance(user, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


CurrentUserDep = Annotated[dict[str, Any], Depends(get_current_user)]


def require_scope(
    scope: str,
) -> Callable[[Request, dict[str, Any]], dict[str, Any]]:
    """Dependency factory requiring ``scope`` in the session scopes.

    Resolution order enforces the 401/403 split: ``get_current_user`` runs
    first as a sub-dependency (401 when unauthenticated); the scope check
    then yields 403 for an authenticated caller lacking the scope. Deny by
    default: a missing or malformed ``scopes`` entry never passes.
    """

    def checker(request: Request, user: CurrentUserDep) -> dict[str, Any]:
        scopes = request.session.get("scopes", [])
        if not isinstance(scopes, list) or scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}",
            )
        return user

    return checker
