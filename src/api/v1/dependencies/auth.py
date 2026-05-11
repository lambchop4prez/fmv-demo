from datetime import datetime
import ssl
from authlib.integrations.starlette_client import OAuth
from joserfc import jwt
from joserfc.jwt import Token
from joserfc.errors import BadSignatureError
from config.oidc import oidc_settings
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import SecurityScopes
from config.oauth import oauth_settings
from models.user import User

from api.v1.dependencies.repository import UserRepositoryDep

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# def jwks_client() -> jwt.PyJWKClient:
#     return jwt.PyJWKClient(oidc_settings.jwks_url, ssl_context=ctx)


# bearer = HTTPBearer()


# async def validate_token(
#     unverified_token: HTTPAuthorizationCredentials | None = Depends(bearer),
#     jwks_client: jwt.PyJWKClient = Depends(jwks_client),
# ) -> dict[str, Any]:
#     if unverified_token is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid authorization token",
#         ) from None
#     try:
#         keyset = jwks_client.get_jwk_set()
#         verified_token = jwt.decode_complete(
#             jwt=unverified_token.credentials,
#             key=keyset[oidc_settings.signing_key_id],
#             algorithms=["RS256"],
#             audience=oidc_settings.audience,
#             issuer=oidc_settings.issuer,
#             options={
#                 # "strict_aud": True,
#                 "enforce_minimum_key_length": True,
#                 "verify_aud": True,
#                 "verify_exp": True,
#                 "verify_iat": True,
#                 "verify_iss": True,
#                 "verify_jti": True,
#                 "verify_nbf": True,
#                 "verify_signature": True,
#                 "verify_sub": True,
#             },
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Unsupported authorization code",
#         ) from None
#     return verified_token


async def oauth_config() -> OAuth:
    oauth = OAuth()
    oauth.register(
        "pocketid",
        client_id=oauth_settings.client_id,
        client_secret=oauth_settings.client_secret,
        issuer=oauth_settings.issuer,
        code_challenge_method="S256",
        server_metadata_url=f"{oauth_settings.issuer}/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email groups", "verify": False},
    )
    return oauth


class UnauthorizedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )


async def valid_token(
    request: Request,
    oauth: OAuth = Depends(oauth_config),
) -> Token:
    client = oauth.create_client("pocketid")
    if (id_token := request.session.get("id_token")) is None:
        raise UnauthorizedError()
    jwks = await client.fetch_jwk_set()
    try:
        decoded = jwt.decode(value=id_token, key=jwks)
    except BadSignatureError:
        raise UnauthorizedError()

    metadata = client.load_server_metadata()
    if decoded.claims["iss"] != metadata["issuer"]:
        raise UnauthorizedError()
    if decoded.claims["aud"] != oidc_settings.audience:
        raise UnauthorizedError()
    exp = datetime.fromtimestamp(decoded.claims["exp"])
    if exp < datetime.now():
        raise UnauthorizedError()
    return decoded


async def current_active_user(
    user_repository: UserRepositoryDep, token: Token = Depends(valid_token)
) -> User:
    sub = token.claims["sub"]
    if (user := (await user_repository.get(sub))) is None:
        raise UnauthorizedError()
    if not user.active:
        raise UnauthorizedError()
    return user


async def validate_scope(
    security_scopes: SecurityScopes, token: Token = Depends(valid_token)
) -> None:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    if not (security_scopes and security_scopes.scopes):
        raise credentials_exception
    scopes = token.claims.get(oidc_settings.role_claims)
    if scopes is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported authorization code",
        )

    if not set(security_scopes.scopes).issubset(set(scopes)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )
