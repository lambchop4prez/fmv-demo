"""Session-wide pytest configuration for the backend suite (src/).

Why this file exists
-------------------
Every settings object in ``config/*`` is an ``@lru_cache`` factory
(``get_session_settings``, ``get_oidc_settings``, ``get_api_settings``,
...). The first call reads ``os.environ`` and the result is frozen for the
lifetime of the process. Imports of ``api`` (via ``api/__init__.py`` ->
``api.main`` -> ``api.v1.api`` -> ``middleware_stack``) instantiate session
and CORS settings at import time. Therefore the safe test defaults below
MUST run before any ``config``/``api`` import. pytest imports the top-level
``conftest.py`` before any test module, which guarantees that ordering.

The defaults make the suite runnable on a clean clone with no secrets: no
``.secrets.env``, no live IdP, no MongoDB. They are hard-set (not
``setdefault``) so tests stay deterministic even when the developer shell
exports real values through ``.mise.toml`` / ``.secrets.env``.

Provider config uses the canonical ``OIDC__*`` env names (prefix
``OIDC__``, nested delimiter ``__``; see ``.secrets.env.example`` and
decisions D2/D3) and points ``static_jwks_file`` at the committed test
JWKS, so token validation is fully offline (decisions D2/D6). The matching
private key (``test/fixtures/oidc_test_private_key.pem``, TEST ONLY, never
production) mints RS256 tokens with ``kid=fmv-test-key-1``.

NOTE: imports of ``config``/``api`` are deliberately deferred into
fixtures. They must not execute before the env defaults above run.
"""

import os
import time
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Callable

import jwt
import pytest
from pytest_mock import MockerFixture

# --- test constants ---------------------------------------------------------
FIXTURES_DIR = Path(__file__).resolve().parent / "test" / "fixtures"
TEST_JWKS_FILE = FIXTURES_DIR / "oidc_test_jwks.json"
TEST_PRIVATE_KEY_FILE = FIXTURES_DIR / "oidc_test_private_key.pem"

TEST_PROVIDER = "test"
TEST_ISSUER = "https://oidc.test/realms/fmv"
TEST_AUDIENCE = "fmv-demo-api"
TEST_CLIENT_ID = "fmv-test-client"
TEST_ROLE_CLAIMS = "groups"
# Fixed kid of the committed test keypair (src/test/fixtures/README.md).
TEST_KID = "fmv-test-key-1"

# --- safe env defaults: MUST precede any config/api import -----------------
os.environ["SESSION_SECRET_KEY"] = "test-only-session-secret-never-a-real-one"
# TestClient talks plain http; a Secure-only cookie would never come back.
os.environ["SESSION_HTTPS_ONLY"] = "false"
# No MongoDB in unit tests; the inmemory stub serves robot routes.
os.environ["BACKEND_REPOSITORY"] = "inmemory"
# Static JWKS stub is dev/CI only; production is rejected fail-closed.
os.environ["BACKEND_ENVIRONMENT"] = "dev"

# Purge any OIDC env inherited from the developer shell (mise loads
# .secrets.env): the test provider below must be the only one configured,
# or tests would depend on machine state.
for _key in [k for k in os.environ if k.upper().startswith("OIDC_")]:
    del os.environ[_key]

# Canonical OIDC__* names (env_prefix="OIDC__", env_nested_delimiter="__").
os.environ["OIDC__DEFAULT_PROVIDER"] = TEST_PROVIDER
os.environ[f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__ISSUER"] = TEST_ISSUER
os.environ[f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__AUDIENCE"] = TEST_AUDIENCE
os.environ[f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__CLIENT_ID"] = TEST_CLIENT_ID
os.environ[f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__ROLE_CLAIMS"] = TEST_ROLE_CLAIMS
os.environ[f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__STATIC_JWKS_FILE"] = str(
    TEST_JWKS_FILE
)


# --- shared fixtures ---------------------------------------------------------
@pytest.fixture
def anyio_backend() -> str:
    """Run ``@pytest.mark.anyio`` tests on asyncio (mirrors pkg test style)."""
    return "asyncio"


@pytest.fixture(scope="session")
def private_key_pem() -> str:
    """PEM text of the committed TEST-only RSA private key (never prod)."""
    return TEST_PRIVATE_KEY_FILE.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def id_token_factory(private_key_pem: str) -> Callable[..., str]:
    """Factory minting RS256 id_tokens signed with the committed test key.

    Tokens carry ``kid=fmv-test-key-1`` so the static JWKS resolver matches
    them offline. ``expires_in`` is seconds from now (negative to mint an
    expired token). ``scopes`` populates the provider ``role_claims`` group
    claim; ``extra`` merges arbitrary claims (e.g. ``name``/``picture``).
    """

    def mint(
        *,
        sub: str = "user-123",
        scopes: Sequence[str] | None = None,
        issuer: str = TEST_ISSUER,
        audience: str = TEST_AUDIENCE,
        kid: str = TEST_KID,
        expires_in: int = 300,
        include_kid: bool = True,
        extra: Mapping[str, Any] | None = None,
    ) -> str:
        issued_at = int(time.time())
        payload: dict[str, Any] = {
            "iss": issuer,
            "aud": audience,
            "sub": sub,
            "iat": issued_at,
            "nbf": issued_at,
            "exp": issued_at + expires_in,
            "jti": f"test-jti-{sub}-{issued_at}",
        }
        if scopes is not None:
            payload[TEST_ROLE_CLAIMS] = list(scopes)
        if extra is not None:
            payload.update(extra)
        headers: dict[str, Any] | None = {"kid": kid} if include_kid else None
        return jwt.encode(payload, private_key_pem, algorithm="RS256", headers=headers)

    return mint


@pytest.fixture
def user_repository(mocker: MockerFixture) -> Any:
    """In-memory user repository fake; no user exists unless staged."""
    from repository import UserRepository

    repository = mocker.AsyncMock(spec=UserRepository)
    repository.get.return_value = None
    return repository


@pytest.fixture
def v1_client(user_repository: Any) -> Iterator[Any]:
    """httpx TestClient over the real ``api.v1.api`` app (with middleware).

    The user repository dependency is overridden with the shared
    ``user_repository`` fake so login never reaches MongoDB. Robot routes
    keep the real ``inmemory`` repository selected by
    ``BACKEND_REPOSITORY=inmemory``. Imports are deferred here so they run
    after the env defaults at the top of this module.
    """
    from fastapi.testclient import TestClient

    from api.v1.api import api
    from api.v1.dependencies.repository import get_user_repository

    api.dependency_overrides[get_user_repository] = lambda: user_repository
    try:
        with TestClient(api, base_url="http://testserver") as client:
            yield client
    finally:
        api.dependency_overrides.clear()
