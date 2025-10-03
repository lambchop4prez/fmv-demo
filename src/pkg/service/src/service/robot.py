from typing import List

from models import Robot
from repository import RobotRepository


class RobotService:
    repository: RobotRepository

    def __init__(self, repository: RobotRepository):
        self.repository = repository

    async def list(self) -> List[Robot]:
        return await self.repository.list()

    async def create(self, robot: Robot) -> None:
        await self.repository.create(robot)
