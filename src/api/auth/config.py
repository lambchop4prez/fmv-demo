from config.api import ApiSettings
from fastapi_oauth2.middleware import OAuth2Config
from fastapi_oauth2.client import Claims, OAuth2Client
from social_core.backends.github import GithubOAuth2


def build_config(settings: ApiSettings):
    return OAuth2Config(
        enable_ssr=False,
        allow_http=True,
        jwt_secret=settings.jwt_secret,
        jwt_expires=settings.jwt_expires,
        jwt_algorithm=settings.jwt_algorithm,
        clients=[
            OAuth2Client(
                backend=GithubOAuth2,
                client_id=settings.oauth2_github_client_id,
                client_secret=settings.oauth2_github_client_secret,
                scope=["user:email"],
                claims=Claims(
                    picture="avatar_url",
                    identity=lambda user: f"{user.provider}:{user.id}",
                ),
            )
        ],
    )
