from typing import Sequence

from pydantic import BaseModel, Field

from .robot import Robot


class RobotCollection(BaseModel):
    robots: Sequence[Robot] = Field([])
