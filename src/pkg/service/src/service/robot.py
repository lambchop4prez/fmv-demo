from typing import Sequence

from models import Robot
from models.robot_profile import RobotProfile
from repository import RobotRepository


class RobotService:
    repository: RobotRepository

    def __init__(self, repository: RobotRepository):
        self.repository = repository

    async def list(self) -> Sequence[Robot]:
        return await self.repository.list()

    async def create(self, robot: RobotProfile) -> None:
        await self.repository.create(robot)

    async def find(self, name: str) -> Robot | None:
        return await self.repository.find(name)
