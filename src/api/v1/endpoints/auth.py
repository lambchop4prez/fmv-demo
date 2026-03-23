import secrets
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response
from config.session import session_settings
from api.v1.dependencies.auth import validate_token

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
    response.set_cookie(
        key=session_settings.session_cookie,
        value=request.session.get("_session_id", secrets.token_urlsafe(32)),
        max_age=session_settings.max_age,
        secure=True,
        httponly=session_settings.https_only,
        samesite=session_settings.same_site,
    )


@router.post("/login")
async def login_session(
    request: Request,
    response: Response,
    token: Dict[str, Any] = Depends(validate_token),
) -> None:
    print(token)
    if token:
        await rotate_session(request, response)


@router.post("/logout")
async def logout(request: Request, response: Response) -> None:
    request.session.clear()
    response.delete_cookie(session_settings.session_cookie)
