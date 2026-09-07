"""API-wide settings.

Built lazily via ``get_api_settings`` so importing this module does not
require secrets (clean-clone CI).

Fail-closed rule: ``static_jwks`` / ``static_jwks_file`` are a dev/CI
static-key stub only. When ``environment`` is ``"production"``, building
these settings rejects any provider that still carries a static JWKS.
"""

from functools import lru_cache
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .oidc import get_oidc_settings


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="BACKEND_", extra="allow", case_sensitive=False
    )
    api_version: Literal["v1"] = "v1"
    repository: Literal["inmemory", "mongodb"] = "inmemory"
    app_name: str = "FMV Demo"
    environment: str = "dev"

    @model_validator(mode="after")
    def reject_static_jwks_in_production(self) -> Self:
        """Static JWKS is a dev/CI stub; never allow it in production."""
        if self.environment != "production":
            return self
        stubbed = sorted(
            name
            for name, provider in get_oidc_settings().providers.items()
            if provider.static_jwks is not None or provider.static_jwks_file is not None
        )
        if stubbed:
            raise ValueError(
                "static_jwks/static_jwks_file are a dev/CI stub and are not "
                "allowed when BACKEND_ENVIRONMENT=production "
                f"(providers: {', '.join(stubbed)})"
            )
        return self


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()
