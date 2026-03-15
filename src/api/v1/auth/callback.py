from fastapi import Depends
from fastapi_oauth2.middleware import Auth, User
from service.user import UserService

from api.dependencies.service import get_user_service

from models import User as UserModel


async def auth_callback(
    auth: Auth, user: User, service: UserService = Depends(get_user_service)
) -> None:
    print("auth_callback")
    if user.identity and not await service.find(user.identity):
        await service.create(
            UserModel(
                **{
                    "identity": user.identity,
                    "username": user.get("username"),
                    "name": user.display_name,
                    "image": user.picture,
                    "email": user.email,
                }
            )
        )
