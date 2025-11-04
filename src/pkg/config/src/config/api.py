from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="BACKEND_", extra="allow", case_sensitive=False
    )
    api_version: Literal["v1"] = "v1"
    repository: Literal["inmemory", "mongodb"] = "inmemory"
    app_name: str = "FMV Demo"
    # module_version: str = importlib.metadata.version("api")


settings = ApiSettings()
