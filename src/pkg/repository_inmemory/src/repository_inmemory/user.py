from models.user import User
from repository import UserRepository

USERS: list[User] = []


class InMemoryUserRepository(UserRepository):
    async def create(self, user: User) -> None:
        USERS.append(user)

    async def find(self, identity: str) -> User | None:
        return next((user for user in USERS if user.identity == identity), None)
