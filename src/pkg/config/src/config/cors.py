from collections.abc import Sequence
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
    allow_credentials: bool = True


cors_settings = CorsSettings()
