from models import User
from repository import UserRepository


class UserService:
    repository: UserRepository

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def exists(self, sub: str) -> bool:
        return (await self.repository.get(sub)) is not None

    async def create(self, user: User) -> User:
        return await self.repository.create(user)

    async def remote(self, user: User) -> None:
        return await self.repository.remove(user)
