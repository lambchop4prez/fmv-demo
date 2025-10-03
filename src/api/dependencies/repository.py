from typing import Annotated

from fastapi import Depends
from pymongo import AsyncMongoClient
from repository import RobotRepository
from repository_inmemory import InMemoryRobotRepository
from repository_mongodb import MongoDbRobotRepository

from ..dependencies.settings import SettingsDep


def get_user_repository(
    settings: SettingsDep,
) -> RobotRepository:
    if settings.REPOSITORY == "inmemory":
        return InMemoryRobotRepository()
    elif settings.REPOSITORY == "mongodb":
        return MongoDbRobotRepository(AsyncMongoClient())
    else:
        raise NotImplementedError(f"Repository {settings.REPOSITORY} not implemented")


RepositoryDep = Annotated[RobotRepository, Depends(get_user_repository)]
