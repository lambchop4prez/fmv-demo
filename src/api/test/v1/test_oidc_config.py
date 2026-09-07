"""Multi-provider OIDC config parsing (plan section 7, unit).

Env names use the canonical ``OIDC__*`` layout (prefix ``OIDC__``, nested
delimiter ``__``; ``.secrets.env.example``, decision D3). The autouse
fixture clears the ``@lru_cache`` on ``get_oidc_settings`` around every
test so ``monkeypatch`` env changes take effect and never leak afterwards.

Constants are repeated here on purpose instead of imported from
``conftest``: two ``conftest.py`` files exist in this workspace and
importing from one by module name is ambiguous.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from config.oidc import get_oidc_settings

TEST_PROVIDER = "test"
TEST_ISSUER = "https://oidc.test/realms/fmv"
TEST_JWKS_FILE = (
    Path(__file__).resolve().parents[3] / "test" / "fixtures" / "oidc_test_jwks.json"
)


@pytest.fixture(autouse=True)
def fresh_oidc_settings() -> Iterator[None]:
    """Reset the cached settings singleton around each test."""
    get_oidc_settings.cache_clear()
    yield
    get_oidc_settings.cache_clear()


def test_conftest_defaults_provide_static_stub_provider() -> None:
    """Safe defaults parse: the suite runs on a clean clone, offline."""
    settings = get_oidc_settings()
    provider = settings.providers[TEST_PROVIDER]
    assert provider.issuer == TEST_ISSUER
    assert provider.static_jwks_file == TEST_JWKS_FILE
    assert provider.static_jwks is None
    # Default provider resolves without a name (dev/CI stub, D2).
    assert settings.resolve_provider() is provider


def test_multi_provider_env_parses_into_providers_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two more providers via env parse into ``providers`` with defaults."""
    monkeypatch.setenv("OIDC__PROVIDERS__ALPHA__ISSUER", "https://alpha.test/realms/a")
    monkeypatch.setenv("OIDC__PROVIDERS__ALPHA__AUDIENCE", "fmv-demo-api")
    monkeypatch.setenv("OIDC__PROVIDERS__BETA__ISSUER", "https://beta.test/realms/b")
    monkeypatch.setenv("OIDC__PROVIDERS__BETA__AUDIENCE", "beta-api")
    monkeypatch.setenv("OIDC__PROVIDERS__BETA__ROLE_CLAIMS", "roles")
    monkeypatch.setenv("OIDC__DEFAULT_PROVIDER", "beta")

    settings = get_oidc_settings()

    assert set(settings.providers) == {TEST_PROVIDER, "alpha", "beta"}
    assert set(settings.provider_names) == {TEST_PROVIDER, "alpha", "beta"}

    beta = settings.providers["beta"]
    assert beta.issuer == "https://beta.test/realms/b"
    assert beta.audience == "beta-api"
    assert beta.role_claims == "roles"
    # Defaults per config.oidc.OidcProviderSettings.
    assert beta.client_id is None
    assert beta.verify_ssl is True
    assert beta.jwks_cache_seconds == 300
    assert beta.static_jwks is None
    assert beta.static_jwks_file is None
    assert beta.jwks_url == "https://beta.test/realms/b/.well-known/jwks.json"
    assert (
        beta.oidc_url == "https://beta.test/realms/b/.well-known/openid-configuration"
    )

    assert settings.providers["alpha"].role_claims == "groups"
    assert settings.default_provider == "beta"


def test_resolve_provider_default_and_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``resolve_provider`` honors the name, then ``default_provider``."""
    monkeypatch.setenv("OIDC__PROVIDERS__GAMMA__ISSUER", "https://gamma.test")
    monkeypatch.setenv("OIDC__PROVIDERS__GAMMA__AUDIENCE", "gamma-api")

    settings = get_oidc_settings()

    assert settings.resolve_provider("gamma") is settings.providers["gamma"]
    assert settings.resolve_provider() is settings.providers[TEST_PROVIDER]

    with pytest.raises(KeyError):
        settings.resolve_provider("does-not-exist")


def test_resolve_provider_single_configured_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With one provider and no default, the sole provider resolves."""
    prefix = f"OIDC__PROVIDERS__{TEST_PROVIDER.upper()}__"
    for suffix in (
        "ISSUER",
        "AUDIENCE",
        "CLIENT_ID",
        "ROLE_CLAIMS",
        "STATIC_JWKS_FILE",
    ):
        monkeypatch.delenv(f"{prefix}{suffix}", raising=False)
    monkeypatch.delenv("OIDC__DEFAULT_PROVIDER", raising=False)

    monkeypatch.setenv("OIDC__PROVIDERS__SOLO__ISSUER", "https://solo.test")
    monkeypatch.setenv("OIDC__PROVIDERS__SOLO__AUDIENCE", "solo-api")

    settings = get_oidc_settings()

    assert set(settings.providers) == {"solo"}
    assert settings.default_provider is None
    assert settings.resolve_provider() is settings.providers["solo"]
