"""Session-exchange endpoint tests: POST /auth/login (plan section 7).

Unit level calls ``login_session`` directly with a session-carrying
``Request`` to assert exactly what lands in ``request.session``. HTTP
level uses the real ``api.v1.api`` TestClient (SessionMiddleware wired,
user repository overridden in ``conftest.v1_client``) for status codes and
the signed session cookie. No live IdP: tokens are minted with the
committed test key and validated against the static JWKS (D2/D6).
"""

from typing import Any

import pytest
from fastapi import HTTPException, Request, status
from models.user import User
from service import UserService

from api.v1.endpoints.auth import login_session

TEST_ISSUER = "https://oidc.test/realms/fmv"


def _session_request() -> Request:
    """A ``Request`` with a pre-populated session scope (middleware-less).

    ``Request.session`` reads ``scope["session"]``; pre-seeding it lets
    ``login_session`` / ``rotate_session`` run without the middleware.
    """
    scope: dict[str, Any] = {
        "type": "http",
        "method": "POST",
        "path": "/auth/login",
        "headers": [],
        "query_string": b"",
        "session": {},
    }
    return Request(scope)


@pytest.fixture
def user_service(user_repository: Any) -> UserService:
    return UserService(user_repository)


# --- unit: what lands in the session ------------------------------------------
@pytest.mark.anyio
async def test_login_session_stores_user_and_scopes(
    user_service: UserService,
) -> None:
    request = _session_request()
    payload = {
        "iss": TEST_ISSUER,
        "sub": "u-1",
        "name": "Unit One",
        "picture": "https://pic.test/u1.png",
        "email": "u1@test.dev",
        "email_verified": True,
        "groups": ["robot:read", "robot:run"],
    }

    user = await login_session(request, user_service, payload)

    assert user.sub == "u-1"
    assert user.active is True
    assert request.session["user"] == user.model_dump()
    assert request.session["user"]["name"] == "Unit One"
    assert request.session["scopes"] == ["robot:read", "robot:run"]


@pytest.mark.anyio
async def test_login_session_missing_optional_claims_does_not_500(
    user_service: UserService,
) -> None:
    """Defect 5 regression: sparse IdP claims must not crash (500)."""
    request = _session_request()
    payload = {"iss": TEST_ISSUER, "sub": "u-sparse", "groups": ["robot:read"]}

    user = await login_session(request, user_service, payload)

    assert user.name == "u-sparse"  # falls back to sub
    assert user.picture == ""
    assert user.email == ""
    assert user.email_verified is False
    assert request.session["scopes"] == ["robot:read"]


@pytest.mark.anyio
async def test_login_session_inactive_user_yields_403(
    user_service: UserService, user_repository: Any
) -> None:
    """Defect 6 regression: soft-deleted accounts cannot re-authenticate."""
    user_repository.get.return_value = User(
        sub="u-gone",
        name="Gone User",
        picture="",
        email="",
        email_verified=False,
        active=False,
    )
    request = _session_request()
    payload = {"iss": TEST_ISSUER, "sub": "u-gone", "groups": ["robot:read"]}

    with pytest.raises(HTTPException) as excinfo:
        await login_session(request, user_service, payload)

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert request.session == {}  # nothing stored for a rejected login


@pytest.mark.anyio
async def test_login_session_missing_sub_yields_401(
    user_service: UserService,
) -> None:
    request = _session_request()
    payload = {"iss": TEST_ISSUER, "groups": ["robot:read"]}

    with pytest.raises(HTTPException) as excinfo:
        await login_session(request, user_service, payload)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_login_session_missing_role_claims_stores_no_scopes(
    user_service: UserService,
) -> None:
    """Deny by default: absent role claims store an empty scope list."""
    request = _session_request()
    payload = {"iss": TEST_ISSUER, "sub": "u-noscope"}

    await login_session(request, user_service, payload)

    assert request.session["scopes"] == []


# --- HTTP level: status codes + signed session cookie -----------------------
def test_login_valid_token_yields_200_and_session_cookie(
    v1_client: Any, id_token_factory: Any
) -> None:
    token = id_token_factory(
        sub="u-http",
        scopes=["robot:read"],
        extra={"name": "Http User"},
    )

    response = v1_client.post(
        "/auth/login", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["sub"] == "u-http"
    assert body["name"] == "Http User"
    assert body["active"] is True
    assert "session" in response.cookies


def test_login_without_bearer_yields_401(v1_client: Any) -> None:
    assert v1_client.post("/auth/login").status_code == status.HTTP_401_UNAUTHORIZED


def test_login_garbage_token_yields_401(v1_client: Any) -> None:
    response = v1_client.post(
        "/auth/login", headers={"Authorization": "Bearer garbage.not.jwt"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user_yields_403(
    v1_client: Any,
    user_repository: Any,
    id_token_factory: Any,
) -> None:
    user_repository.get.return_value = User(
        sub="u-inactive",
        name="Inactive",
        picture="",
        email="",
        email_verified=False,
        active=False,
    )
    token = id_token_factory(sub="u-inactive", scopes=["robot:read"])

    response = v1_client.post(
        "/auth/login", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_login_sparse_claims_yields_200_not_500(
    v1_client: Any, id_token_factory: Any
) -> None:
    """Defect 5 at the HTTP boundary: no name/picture/email, no crash."""
    token = id_token_factory(sub="u-sparse-http", scopes=["robot:read"])

    response = v1_client.post(
        "/auth/login", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["name"] == "u-sparse-http"
    assert body["picture"] == ""
    assert body["email"] == ""
    assert body["email_verified"] is False


# --- HTTP level: GET /auth/session (guard probe) ----------------------------
def test_session_with_cookie_yields_200_and_user(
    v1_client: Any, id_token_factory: Any
) -> None:
    """After the login exchange the cookie alone answers 200 with the user."""
    token = id_token_factory(
        sub="u-session", scopes=["robot:read"], extra={"name": "Session User"}
    )
    v1_client.post("/auth/login", headers={"Authorization": f"Bearer {token}"})

    response = v1_client.get("/auth/session")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["sub"] == "u-session"
    assert body["name"] == "Session User"


def test_session_without_cookie_yields_401(v1_client: Any) -> None:
    """No session cookie: the guard probe must answer 401, not 200."""
    assert v1_client.get("/auth/session").status_code == status.HTTP_401_UNAUTHORIZED
