from typing import List

from pydantic import BaseModel, Field

from .robot import Robot


class RobotCollection(BaseModel):
    robots: List[Robot] = Field([])
