from models.user import User
from repository.user import UserRepository
from repository_mongodb.models import UserDocument


class MongoDbUserRepository(UserRepository):
    async def create(self, user: User) -> None:
        await UserDocument.insert_one(UserDocument(**user.model_dump()))

    async def find(self, identity: str) -> User | None:
        if (item := await UserDocument.find_one({"identity": identity})) is None:
            return None
        return User(**item.model_dump())
