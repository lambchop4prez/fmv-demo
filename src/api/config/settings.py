from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_")
    API_VERSION: Literal["v1"] = "v1"
    REPOSITORY: Literal["inmemory", "mongodb"] = "inmemory"
    PROJECT_NAME: str = "FMV Demo"
