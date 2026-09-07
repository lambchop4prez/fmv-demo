"""Session exchange endpoints (token→session exchange, decision D1=a).

``POST /auth/login`` is the only bearer-consuming route: it validates the
IdP token via ``validate_token`` (which returns the decoded payload, not
the ``decode_complete`` envelope), upserts the user, and stores the identity
plus scopes in the signed session cookie. All other protected routes
authenticate through that cookie via
``api.v1.dependencies.session.get_current_user`` / ``require_scope``.

Token introspection remains the documented upgrade path (plan decision D2)
for revocation within token lifetime; it is not implemented here.
"""

from typing import Annotated, Any

from config.session import get_session_settings
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from models.user import User

from api.v1.dependencies.auth import route_provider_by_iss, validate_token
from api.v1.dependencies.service import UserServiceDep
from api.v1.dependencies.session import CurrentUserDep

router = APIRouter()


def rotate_session(request: Request) -> None:
    """Rotate the session: clear, then repopulate ``request.session``.

    Starlette's ``SessionMiddleware`` serializes the session into the signed
    cookie and sets it on the response after the handler returns, so no
    manual ``set_cookie`` belongs here. The previous manual cookie wrote a
    nonexistent ``_session_id`` value (Starlette sessions have no session
    id) and coupled ``HttpOnly`` to ``https_only``; the middleware already
    sets ``HttpOnly`` unconditionally.
    """
    session_data = dict(request.session)
    request.session.clear()
    request.session.update(session_data)


def _session_scopes(payload: dict[str, Any]) -> list[str]:
    """Scopes to store in the session, from the provider's role claims.

    The provider is resolved from the already-verified ``iss`` claim
    (decision D3 names the claim via ``role_claims``). Space-delimited
    scope strings are normalized to lists; a missing or malformed claim
    yields an empty list, which denies all scoped routes (deny by default).
    """
    _, provider = route_provider_by_iss(payload.get("iss"))
    claims = payload.get(provider.role_claims)
    if isinstance(claims, str):
        return claims.split()
    if isinstance(claims, list):
        return [claim for claim in claims if isinstance(claim, str)]
    return []


@router.post("/login")
async def login_session(
    request: Request,
    service: UserServiceDep,
    payload: Annotated[dict[str, Any], Depends(validate_token)],
) -> User:
    """Exchange a bearer id_token for a session cookie.

    This is the only bearer-consuming route (D1=a); afterwards the browser
    authenticates with the session cookie alone.
    """
    # `payload` is the validated JWT payload (not a decode_complete
    # envelope). `sub` is the only mandatory claim: without a subject the
    # caller cannot be identified, so fail closed with 401.
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing a subject (sub) claim",
        )

    # Defensive claim mapping: IdPs routinely omit optional claims, and
    # `User(**payload)` would raise pydantic ValidationError (HTTP 500).
    user = User(
        sub=sub,
        name=payload.get("name") or payload.get("preferred_username") or sub,
        picture=payload.get("picture") or "",
        email=payload.get("email") or "",
        email_verified=bool(payload.get("email_verified", False)),
    )

    existing = await service.get(sub)
    if existing is not None and not existing.active:
        # Soft-deleted accounts remain in the store with active=False and
        # must not re-authenticate silently (defect 6).
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled"
        )

    # Reaching this point means active: new users are created active,
    # existing users were verified active above.
    user.active = True
    if existing is None:
        await service.create(user)

    request.session["user"] = user.model_dump()
    request.session["scopes"] = _session_scopes(payload)
    rotate_session(request)
    return user


@router.get("/session")
async def read_session(user: CurrentUserDep) -> dict[str, Any]:
    """Return the session user, or 401 when no valid session cookie exists.

    Additive endpoint (v1) for the frontend auth guard: IdP tokens live in
    memory only (decision D4), so ``getUser()`` is empty after a page reload
    even while the signed session cookie (D1=a) is still valid. The guard
    probes this cookie-authenticated route before redirecting to /login;
    ``get_current_user`` yields 401 when the session is absent or tampered.
    """
    return user


@router.post("/logout")
async def logout(request: Request, response: Response) -> None:
    request.session.clear()
    response.delete_cookie(get_session_settings().session_cookie, path="/")
