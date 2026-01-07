from typing import Sequence

from models import Robot, RobotProfile
from pymongo import AsyncMongoClient
from repository import RobotRepository

from .models import RobotDocument, RobotTaskDocument


class MongoDbRobotRepository(RobotRepository):
    def __init__(self, client: AsyncMongoClient):
        self.db = client.get_database("app")
        self.collection = self.db.get_collection("robot")

    async def list(self) -> Sequence[Robot]:
        return await RobotDocument.find_all(limit=1000).project(Robot).to_list()

    async def create(self, robot: RobotProfile) -> None:
        await RobotDocument.insert_one(RobotDocument(**robot.model_dump()))

    async def find(self, name: str) -> RobotProfile | None:
        if (item := await RobotDocument.find_one({"name": name})) is None:
            return None
        tasks = RobotTaskDocument.find_all({"robot": item.name})
        return RobotProfile(tasks=tasks, **item.model_dump())
