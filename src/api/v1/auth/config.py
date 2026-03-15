from config.auth import auth_settings
from config.oauth import oauth2_settings
from fastapi_oauth2.middleware import OAuth2Config
from fastapi_oauth2.client import Claims, OAuth2Client
from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2


oauth2_config = OAuth2Config(
    enable_ssr=False,
    allow_http=True,
    jwt_secret=auth_settings.jwt_secret,
    jwt_expires=auth_settings.jwt_expires,
    jwt_algorithm=auth_settings.jwt_algorithm,
    clients=[
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=oauth2_settings.github_client_id,
            client_secret=oauth2_settings.github_client_secret,
            scope=["user:email"],
            claims=Claims(
                picture="avatar_url",
                identity=lambda user: f"{user.provider}:{user.id}",
            ),
        ),
        OAuth2Client(
            backend=GoogleOAuth2,
            redirect_uri="http://localhost:8000/api/v1/oauth2/google-oauth2/token",
            client_id=oauth2_settings.google_client_id,
            client_secret=oauth2_settings.google_client_secret,
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
    ],
)
