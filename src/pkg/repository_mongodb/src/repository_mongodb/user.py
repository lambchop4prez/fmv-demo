from typing import Sequence
from beanie.odm.operators.update.general import Set

from models import User
from repository import UserRepository
from repository_mongodb.models import UserDocument


class MongoDbUserRepository(UserRepository):
    async def get(self, sub: str) -> User | None:
        if item := await UserDocument.find_one({"sub": sub}).project(User):
            return item
        return None

    async def list(self) -> Sequence[User]:
        return (
            await UserDocument.find_many({"active": True}, limit=100)
            .project(User)
            .to_list()
        )

    async def create(self, user: User) -> User:
        if (
            item := await UserDocument.insert_one(UserDocument(**user.model_dump()))
        ) is None:
            raise RuntimeError("Failed to create user")
        return User(**item.model_dump())

    async def remove(self, sub: str) -> None:
        if (u := await UserDocument.find_one({"sub": sub})) is None:
            raise RuntimeError("User not found")
        await u.update(Set({UserDocument.active: False}))
