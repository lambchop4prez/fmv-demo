from abc import abstractmethod
from typing import Protocol, Sequence

from models import User


class UserRepository(Protocol):
    @abstractmethod
    async def get(self, sub: str) -> User:
        raise NotImplementedError()

    @abstractmethod
    async def list(self) -> Sequence[User]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, sub: str) -> None:
        raise NotImplementedError()
