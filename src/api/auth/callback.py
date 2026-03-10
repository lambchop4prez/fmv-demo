from fastapi_oauth2.middleware import Auth, User

from api.dependencies.service import UserServiceDep


async def auth_callback(auth: Auth, user: User, service: UserServiceDep) -> None:
    if user.identity and not await service.find(user.identity):
        await service.create(
            User(
                **{
                    "identity": user.identity,
                    "username": user.get("username"),
                    "name": user.display_name,
                    "image": user.picture,
                    "email": user.email,
                }
            )
        )
