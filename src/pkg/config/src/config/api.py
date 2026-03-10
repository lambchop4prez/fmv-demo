from collections.abc import Sequence
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_",
        extra="allow",
        case_sensitive=False,
    )
    api_version: Literal["v1"] = "v1"
    repository: Literal["inmemory", "mongodb"] = "inmemory"
    app_name: str = "FMV Demo"
    allow_origins: Sequence[str] = [""]
    allow_methods: Sequence[str] = ["*"]
    allow_headers: Sequence[str] = ["*"]
    allow_credentials: bool = False
    jwt_secret: str = ""
    jwt_expires: int = 900
    jwt_algorithm: str = "HS256"
    oauth2_github_client_id: str = ""
    oauth2_github_client_secret: str = ""

    # module_version: str = importlib.metadata.version("api")


settings = ApiSettings()
