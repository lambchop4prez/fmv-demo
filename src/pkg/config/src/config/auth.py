from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AUTH_",
        extra="allow",
        case_sensitive=False,
    )
    jwt_secret: str = ""
    jwt_expires: int = 900
    jwt_algorithm: str = "HS256"


auth_settings = AuthSettings()
