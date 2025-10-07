from abc import abstractmethod
from typing import List, Protocol

from models import Robot


class RobotRepository(Protocol):
    @abstractmethod
    async def list(self) -> List[Robot]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, robot: Robot) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def find(self, name: str) -> Robot:
        raise NotImplementedError()
