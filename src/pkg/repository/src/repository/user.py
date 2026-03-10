from abc import abstractmethod
from typing import Protocol

from models import User


class UserRepository(Protocol):
    @abstractmethod
    async def create(self, user: User) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def find(self, identity: str) -> User | None:
        raise NotImplementedError()
