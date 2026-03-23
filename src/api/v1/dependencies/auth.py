import ssl
from typing import Annotated, Any

from config.oidc import oidc_settings
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)
import jwt

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(oidc_settings.jwks_url, ssl_context=ctx)


bearer = HTTPBearer()


async def validate_token(
    unverified_token: HTTPAuthorizationCredentials | None = Depends(bearer),
    jwks_client: jwt.PyJWKClient = Depends(jwks_client),
) -> dict[str, Any]:
    if unverified_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization token",
        ) from None
    try:
        keyset = jwks_client.get_jwk_set()
        verified_token = jwt.decode_complete(
            jwt=unverified_token.credentials,
            key=keyset[oidc_settings.signing_key_id],
            algorithms=["RS256"],
            audience=oidc_settings.audience,
            issuer=oidc_settings.issuer,
            options={
                # "strict_aud": True,
                "enforce_minimum_key_length": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_jti": True,
                "verify_nbf": True,
                "verify_signature": True,
                "verify_sub": True,
            },
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported authorization code",
        ) from None
    return verified_token


async def validate_scope(
    security_scopes: SecurityScopes,
    token: Annotated[dict[str, Any], Depends(validate_token)],
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
    scopes = token.get(oidc_settings.role_claims)
    if scopes is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported authorization code",
        )

    if not set(security_scopes.scopes).issubset(set(scopes)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )
