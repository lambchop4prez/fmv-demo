from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_nested_max_split=1,
        env_prefix="OAUTH_",
        extra="allow",
        case_sensitive=False,
    )
    client_id: str
    client_secret: str
    issuer: Optional[str]


oauth_settings = OAuthSettings()
