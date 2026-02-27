from typing import Optional, Sequence

from .robot import Robot
from .robot_task import RobotTask


class RobotProfile(Robot):
    description: str
    tasks: Optional[Sequence[RobotTask]] = []
