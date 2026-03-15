from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuth2Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OAUTH2_",
        extra="allow",
        case_sensitive=False,
    )
    github_client_id: str = ""
    github_client_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""


oauth2_settings = OAuth2Settings()
