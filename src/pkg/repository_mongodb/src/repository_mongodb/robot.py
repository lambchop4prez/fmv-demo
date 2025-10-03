from typing import List

from models import Robot
from pymongo import AsyncMongoClient
from repository import RobotRepository


class MongoDbRobotRepository(RobotRepository):
    def __init__(self, client: AsyncMongoClient):
        self.db = client.get_database("app")
        self.collection = self.db.get_collection("user")

    async def list(self) -> List[Robot]:
        return await self.collection.find().to_list(1000)

    async def create(self, robot: Robot) -> None:
        await self.collection.insert_one(robot)
