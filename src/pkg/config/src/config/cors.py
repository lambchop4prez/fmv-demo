"""CORS settings.

Built lazily via ``get_cors_settings`` so importing this module performs no
required configuration work (clean-clone CI).
"""

from collections.abc import Sequence
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CORS_",
        extra="allow",
        case_sensitive=False,
    )
    allow_origins: Sequence[str] = [""]
    allow_methods: Sequence[str] = ["*"]
    allow_headers: Sequence[str] = ["*"]
    allow_credentials: bool = False


@lru_cache
def get_cors_settings() -> CorsSettings:
    return CorsSettings()
