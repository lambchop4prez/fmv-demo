"""Session cookie settings.

Built lazily via ``get_session_settings`` so importing this module does not
require ``SESSION_SECRET_KEY`` (clean-clone CI). Construction fails closed
when the secret is missing.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="SESSION_", extra="allow"
    )
    secret_key: str
    session_cookie: str = "session"
    max_age: int = 1800  # 30 minutes
    same_site: Literal["lax", "strict", "none"] = "strict"
    https_only: bool = True


@lru_cache
def get_session_settings() -> SessionSettings:
    return SessionSettings()
