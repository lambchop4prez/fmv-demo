from abc import abstractmethod
from typing import Protocol, Sequence

from models import Robot
from models.robot_profile import RobotProfile


class RobotRepository(Protocol):
    @abstractmethod
    async def list(self) -> Sequence[Robot]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, robot: RobotProfile) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def find(self, name: str) -> RobotProfile | None:
        raise NotImplementedError()
