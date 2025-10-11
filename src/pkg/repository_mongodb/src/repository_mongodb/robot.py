from typing import List

from models import Robot
from pymongo import AsyncMongoClient
from repository import RobotRepository


class MongoDbRobotRepository(RobotRepository):
    def __init__(self, client: AsyncMongoClient):
        self.db = client.get_database("app")
        self.collection = self.db.get_collection("robot")

    async def list(self) -> List[Robot]:
        return await self.collection.find().to_list(1000)

    async def create(self, robot: Robot) -> None:
        await self.collection.insert_one(robot.model_dump())

    async def find(self, name: str) -> Robot | None:
        if (item := await self.collection.find_one({"name": name})) is None:
            return None
        return Robot(**item)
