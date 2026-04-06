from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="SESSION_", extra="allow"
    )
    secret_key: str
    session_cookie: str = "session"
    max_age: int = 1800  # 30 minutes
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False


session_settings = SessionSettings()
