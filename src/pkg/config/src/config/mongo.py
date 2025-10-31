from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="BACKEND_MONGO_", extra="allow"
    )
    HOST: str = "localhost"


settings = MongoSettings()
