from typing import List

from models import Robot
from repository import RobotRepository

ROBOTS = [
    {"name": "Bender", "is_great": "true"},
    {"name": "Wall-E"},
    {"name": "Crow T. Robot"},
]


class InMemoryRobotRepository(RobotRepository):
    async def list(self) -> List[Robot]:
        return ROBOTS

    async def create(self, robot: Robot):
        ROBOTS.append(robot)
