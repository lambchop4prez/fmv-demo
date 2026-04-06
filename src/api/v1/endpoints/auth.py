import secrets
from typing import Any, Dict, Literal

from config.api import ApiSettings
from fastapi import APIRouter, Depends, Request, Response
from config.session import session_settings
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from models.user import User
from api.v1.dependencies.auth import oauth_config, validate_token
from api.v1.dependencies.service import UserServiceDep
from api.v1.dependencies.settings import load_settings

router = APIRouter()


# async def introspect_token(valid_token: str):
#     async with httpx.AsyncClient() as client:
#         response = await client.get(oidc_settings.oidc_url)
#         introspection_endpoint = response.json().get("introspection_endpoint")
#         introspection = await client.post(
#             introspection_endpoint, {"token": valid_token}
#         )


async def rotate_session(request: Request, response: Response) -> None:
    session_data = dict(request.session)
    request.session.clear()
    response.delete_cookie(session_settings.session_cookie, path="/")

    # repopulate session and set new cookie
    for key, value in session_data.items():
        request.session[key] = value

    new_session_id = secrets.token_urlsafe(32)
    print(new_session_id)
    response.set_cookie(
        key=session_settings.session_cookie,
        value=new_session_id,
        max_age=session_settings.max_age,
        secure=session_settings.https_only,
        httponly=True,
        samesite=session_settings.same_site,
    )


@router.post("/login")
async def login_session(
    request: Request,
    response: Response,
    service: UserServiceDep,
    token: Dict[str, Any] = Depends(validate_token),
) -> User | None:
    if (payload := token.get("payload")) is not None:
        user = User(**payload)
        if not (await service.exists(user.sub)):
            user.active = True
            await service.create(user)
        await rotate_session(request, response)
        return user
    return None


@router.get("/{provider}/login")
async def oauth_login(
    provider: Literal["google", "github", "pocketid"],
    request: Request,
    oauth: OAuth = Depends(oauth_config),
) -> RedirectResponse:
    client = oauth.create_client(provider)
    redirect_url = request.url_for("oauth_callback", provider=provider)
    return await client.authorize_redirect(request, redirect_url)


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: Literal["google", "github", "pocketid"],
    request: Request,
    response: Response,
    oauth: OAuth = Depends(oauth_config),
    settings: ApiSettings = Depends(load_settings),
) -> RedirectResponse:
    client = oauth.create_client(provider)
    print(request.session)
    try:
        token = await client.authorize_access_token(request)
        request.session["userinfo"] = token.get("userinfo")
    except OAuthError:
        return RedirectResponse(url=f"{settings.frontend_base_url}/error")
    await rotate_session(request, response)
    return RedirectResponse(url=settings.frontend_base_url)


@router.post("/logout")
async def logout(request: Request, response: Response) -> None:
    request.session.clear()
    response.delete_cookie(session_settings.session_cookie)
