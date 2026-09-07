"""MongoDB connection settings.

Built lazily via ``get_mongo_settings`` so importing this module performs no
required configuration work (clean-clone CI).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="BACKEND_MONGO_", extra="allow"
    )
    HOST: str = "localhost"
    DATABASE: str = "robot"


@lru_cache
def get_mongo_settings() -> MongoSettings:
    return MongoSettings()
