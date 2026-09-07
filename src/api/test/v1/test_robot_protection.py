"""Robot router protection tests (plan section 7, endpoint level).

The robot router is protected at router level by ``get_current_user``
(session cookie, 401) and per-route by ``require_scope`` (403, decision
D3). Bearer tokens are exchanged for the session at ``POST /auth/login``
only (decision D1=a); these tests exercise exactly that flow with the
real ``api.v1.api`` app, static JWKS validation, and the ``inmemory``
robot repository. No live IdP, no MongoDB.
"""

from typing import Any

from fastapi import status

from api.v1.scopes import ROBOT_READ, ROBOT_RUN, ROBOT_WRITE


def test_scope_constants_are_the_idp_contract() -> None:
    """Scope strings are the IdP role contract (decision D3): stable."""
    assert (ROBOT_READ, ROBOT_WRITE, ROBOT_RUN) == (
        "robot:read",
        "robot:write",
        "robot:run",
    )


def _login(client: Any, id_token_factory: Any, sub: str, scopes: list[str]) -> None:
    """Exchange a minted token for the session cookie on the client."""
    token = id_token_factory(sub=sub, scopes=scopes)
    response = client.post("/auth/login", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK


def test_robot_list_without_session_yields_401(v1_client: Any) -> None:
    assert v1_client.get("/robot/").status_code == status.HTTP_401_UNAUTHORIZED


def test_robot_find_without_session_yields_401(v1_client: Any) -> None:
    assert v1_client.get("/robot/Bender").status_code == status.HTTP_401_UNAUTHORIZED


def test_robot_run_without_session_yields_401(v1_client: Any) -> None:
    response = v1_client.post("/robot/Bender/run")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_robot_list_wrong_scope_yields_403(
    v1_client: Any, id_token_factory: Any
) -> None:
    """Authenticated but missing ``robot:read``: 403 per RFC 9110."""
    _login(v1_client, id_token_factory, "u-wrong-scope", ["nothing:allowed"])

    assert v1_client.get("/robot/").status_code == status.HTTP_403_FORBIDDEN


def test_robot_list_with_read_scope_yields_200(
    v1_client: Any, id_token_factory: Any
) -> None:
    _login(v1_client, id_token_factory, "u-reader", [ROBOT_READ])

    response = v1_client.get("/robot/")

    assert response.status_code == status.HTTP_200_OK
    names = [robot["name"] for robot in response.json()["robots"]]
    assert "Bender" in names


def test_robot_find_with_read_scope_yields_200(
    v1_client: Any, id_token_factory: Any
) -> None:
    _login(v1_client, id_token_factory, "u-reader", [ROBOT_READ])

    response = v1_client.get("/robot/Bender")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Bender"


def test_robot_run_with_read_scope_yields_403(
    v1_client: Any, id_token_factory: Any
) -> None:
    """Read scope must not imply run scope (least privilege, D3)."""
    _login(v1_client, id_token_factory, "u-reader", [ROBOT_READ])

    response = v1_client.post("/robot/Bender/run")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_robot_create_with_read_scope_yields_403(
    v1_client: Any, id_token_factory: Any
) -> None:
    """Read scope must not imply write scope (least privilege, D3)."""
    _login(v1_client, id_token_factory, "u-reader", [ROBOT_READ])

    response = v1_client.post("/robot/", json={"name": "Malicious Robot"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_robot_run_denied_before_handler_reaches_broker(
    v1_client: Any, id_token_factory: Any
) -> None:
    """Missing ``robot:run`` yields 403 before the Celery publish runs.

    A run with the correct scope would publish to RabbitMQ
    (``RobotService.start`` -> ``primes.delay``), which unit tests never
    touch; denial happens in dependency resolution, ahead of the handler.
    """
    _login(v1_client, id_token_factory, "u-reader", [ROBOT_READ])

    response = v1_client.post("/robot/Bender/run")

    assert response.status_code == status.HTTP_403_FORBIDDEN
