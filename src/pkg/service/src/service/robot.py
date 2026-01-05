import random
from multiprocessing.pool import AsyncResult
from typing import Sequence

from models import Robot
from models.robot_profile import RobotProfile
from repository import RobotRepository
from workers.tasks import primes


class RobotService:
    repository: RobotRepository

    def __init__(self, repository: RobotRepository):
        self.repository = repository

    async def list(self) -> Sequence[Robot]:
        return await self.repository.list()

    async def create(self, robot: RobotProfile) -> None:
        await self.repository.create(robot)

    async def find(self, name: str) -> RobotProfile | None:
        return await self.repository.find(name)

    async def start(self, robot: Robot) -> AsyncResult:
        return primes.delay(robot.name, random.randint(3000000, 3500000))

    # async def tasks(self, robot: Robot) -> Sequence[Task] | None:
