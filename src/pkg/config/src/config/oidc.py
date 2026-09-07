"""OIDC provider settings, multi-provider capable.

Settings are built lazily via ``get_oidc_settings`` so that importing this
module never requires secrets (clean-clone CI). Providers are declared with
nested env vars, e.g.::

    OIDC__PROVIDERS__KEYCLOAK__ISSUER=https://localhost:8443/realms/fmv
    OIDC__PROVIDERS__KEYCLOAK__AUDIENCE=fmv-demo-api
    OIDC__DEFAULT_PROVIDER=keycloak

``static_jwks`` / ``static_jwks_file`` support the dev/CI static-key stub:
tokens are verified against a committed public JWKS, no live IdP required.
Production use is rejected by the fail-closed validator in ``ApiSettings``.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class OidcProviderSettings(BaseModel):
    """Connection and validation settings for a single OIDC provider."""

    issuer: str
    audience: str
    client_id: str | None = None
    role_claims: str = "groups"
    jwks_cache_seconds: int = 300
    verify_ssl: bool = True
    static_jwks: dict[str, Any] | None = None
    static_jwks_file: Path | None = None

    @property
    def oidc_url(self) -> str:
        return f"{self.issuer}/.well-known/openid-configuration"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"


class OpenIdConnectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        # Prefix is "OIDC__" (not "OIDC_") so the canonical env names
        # OIDC__PROVIDERS__<NAME>__* and OIDC__DEFAULT_PROVIDER match:
        # pydantic-settings builds candidates as prefix + field +
        # delimiter, i.e. "OIDC_" + "providers" + "__" would require
        # OIDC_PROVIDERS__<NAME>__* and silently ignore OIDC__* names.
        env_prefix="OIDC__",
        env_nested_delimiter="__",
        extra="allow",
    )
    providers: dict[str, OidcProviderSettings]
    default_provider: str | None = None

    @property
    def provider_names(self) -> list[str]:
        return list(self.providers)

    def resolve_provider(self, name: str | None = None) -> OidcProviderSettings:
        """Look up a provider by name, falling back to ``default_provider``,
        then to the sole configured provider.

        Raises ``KeyError`` when nothing matches (fail closed). Issuer-based
        routing from the token ``iss`` claim is added in the token-validation
        task; this lookup covers the default/single-provider case today.
        """
        key = name or self.default_provider
        if key is None:
            if len(self.providers) == 1:
                return next(iter(self.providers.values()))
            raise KeyError(
                "No OIDC provider configured: set OIDC__PROVIDERS__<NAME>__* "
                "and OIDC__DEFAULT_PROVIDER"
            )
        if key not in self.providers:
            raise KeyError(
                f"Unknown OIDC provider '{key}'; "
                f"configured providers: {', '.join(self.provider_names) or '(none)'}"
            )
        return self.providers[key]


@lru_cache
def get_oidc_settings() -> OpenIdConnectSettings:
    return OpenIdConnectSettings()
