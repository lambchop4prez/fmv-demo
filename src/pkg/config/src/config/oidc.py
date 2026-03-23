from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenIdConnectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="OIDC_", extra="allow"
    )
    issuer: str
    audience: str
    signing_key_id: str
    role_claims: str = "groups"
    expire_seconds: int = 3600

    @property
    def oidc_url(self) -> str:
        return f"{self.issuer}/.well-known/openid-configuration"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"


oidc_settings = OpenIdConnectSettings()
