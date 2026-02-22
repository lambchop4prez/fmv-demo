from pydantic_settings import BaseSettings, SettingsConfigDict


class BrokerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_BROKER_",
        extra="allow",
        case_sensitive=False,
    )
    host: str = "localhost"
    user: str | None = None
    password: str | None = None

    @property
    def url(self) -> str:
        if self.user is None:
            return f"amqp://{self.host}"
        return f"amqp://{self.user}:{self.password}@{self.host}"
