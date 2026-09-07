from models import User
from repository import UserRepository


class UserService:
    repository: UserRepository

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def exists(self, sub: str) -> bool:
        return (await self.repository.get(sub)) is not None

    async def get(self, sub: str) -> User | None:
        # Login needs the stored user (not just existence) to enforce the
        # active check: soft-deleted users stay in the store with
        # active=False and must not re-authenticate silently.
        return await self.repository.get(sub)

    async def create(self, user: User) -> User:
        return await self.repository.create(user)

    async def remote(self, sub: str) -> None:
        await self.repository.remove(sub)
