from typing import Literal

from config.api import ApiSettings
from fastapi import APIRouter, Depends, Request, Response
from config.session import session_settings
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from models.user import User
from api.v1.dependencies.auth import oauth_config
from api.v1.dependencies.service import UserServiceDep
from api.v1.dependencies.settings import load_settings

router = APIRouter()


async def rotate_session(request: Request, response: Response) -> None:
    session_data = dict(request.session)
    request.session.clear()
    response.delete_cookie(session_settings.session_cookie, path="/")

    # repopulate session and set new cookie
    for key, value in session_data.items():
        request.session[key] = value

    # new_session_id = secrets.token_urlsafe(32)
    # print(new_session_id)
    # response.set_cookie(
    #     key=session_settings.session_cookie,
    #     value=new_session_id,
    #     max_age=session_settings.max_age,
    #     secure=session_settings.https_only,
    #     httponly=True,
    #     samesite=session_settings.same_site,
    # )


# @router.post("/login")
# async def login_session(
#     request: Request,
#     response: Response,
#     service: UserServiceDep,
#     token: Dict[str, Any] = Depends(validate_token),
# ) -> User | None:
#     if (payload := token.get("payload")) is not None:
#         user = User(**payload)
#         if not (await service.exists(user.sub)):
#             user.active = True
#             await service.create(user)
#         await rotate_session(request, response)
#         return user
#     return None


@router.get("/{provider}/login")
async def oauth_login(
    provider: Literal["google", "github", "pocketid"],
    request: Request,
    oauth: OAuth = Depends(oauth_config),
) -> RedirectResponse:
    client = oauth.create_client(provider)
    redirect_url = request.url_for("oauth_callback", provider=provider)
    return await client.authorize_redirect(request, redirect_url)  # type: ignore


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: Literal["google", "github", "pocketid"],
    request: Request,
    response: Response,
    user_service: UserServiceDep,
    oauth: OAuth = Depends(oauth_config),
    settings: ApiSettings = Depends(load_settings),
) -> RedirectResponse:
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url=f"{settings.frontend_base_url}/error")

    if (userinfo := token.get("userinfo")) is None:
        return RedirectResponse(url=f"{settings.frontend_base_url}/error")

    user_dict = dict(userinfo)
    sub = user_dict["sub"]
    if await user_service.exists(sub):
        # No user in repository, register user
        user = User(**user_dict)
        user.active = True
        await user_service.create(user)

    request.session["id_token"] = token.get("id_token")
    request.session["refresh_token"] = token.get("refresh_token")
    return RedirectResponse(
        url=settings.frontend_base_url,
    )


@router.post("/logout")
async def logout(request: Request, response: Response) -> None:
    request.session.clear()
    response.delete_cookie(session_settings.session_cookie)
