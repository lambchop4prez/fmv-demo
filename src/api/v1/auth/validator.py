from typing import Optional

from cachetools import TTLCache
from fastapi import HTTPException
from fastapi.security import HTTPBearer, SecurityScopes
import httpx
from jose import JWTError, jwt
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from api.v1.auth.credentials import AccessTokenCredentials


class AccessTokenValidator(HTTPBearer):
    def __init__(
        self,
        *,
        jwks_url: str,
        audience: str,
        issuer: str,
        expire_seconds: int = 3600,
        roles_claim: str = "groups",
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(scheme_name=scheme_name, description=description)
        self.uri = jwks_url
        self.audience = audience
        self.issuer = issuer
        self.roles_claim = roles_claim
        self.keyset_cache: TTLCache[str, str] = TTLCache(16, expire_seconds)

    async def get_jwt_keyset(self) -> str:
        if result := self.keyset_cache.get(self.uri) is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.uri)
                result = self.keyset_cache[self.uri] = response.text
        return result

    async def __call__(self, request, security_scopes: SecurityScopes):
        unverified_token = await super().__call__(request)
        access_token = unverified_token.credentials
        try:
            keyset = await self.get_jwt_keyset()
            verified_token = jwt.decode(
                token=access_token,
                key=keyset,
                audience=self.audience,
                issuer=self.issuer,
            )
        except JWTError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Unsupported authorization code",
            ) from None

        if security_scopes and security_scopes.scopes:
            scopes = verified_token.get(self.roles_claim)
            if scopes is None:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Unsupported authorization code",
                )

            if not set(security_scopes.scopes).issubset(set(scopes)):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not Authorized"
                )

        return AccessTokenCredentials(
            scheme=self.scheme_name, credentials=access_token, token=verified_token
        )
