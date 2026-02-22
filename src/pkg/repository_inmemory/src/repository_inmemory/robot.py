from typing import Sequence

from models import Robot
from models.robot_profile import RobotProfile
from repository import RobotRepository

ROBOTS = [
    RobotProfile(
        name="Bender",
        is_great=True,
        location="Earth",
        description="Please insert girder",
        tasks=None,
    ),
    RobotProfile(
        name="Crow T. Robot",
        is_great=False,
        location="Satellite of Love",
        description="You know you want me baby",
        tasks=None,
    ),
    RobotProfile(
        name="Wall-E",
        is_great=False,
        location="Earth",
        description=" Waste Allocation Load Lifter: Earth-class",
        tasks=None,
    ),
]


class InMemoryRobotRepository(RobotRepository):
    async def list(self) -> Sequence[Robot]:
        return ROBOTS

    async def create(self, robot: RobotProfile) -> None:
        ROBOTS.append(robot)

    async def find(self, name: str) -> RobotProfile | None:
        return next((robot for robot in ROBOTS if robot.name == name), None)
