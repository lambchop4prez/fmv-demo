from typing import Annotated

from fastapi import Depends
from pymongo import AsyncMongoClient
from repository import RobotRepository
from repository_inmemory import InMemoryRobotRepository
from repository_mongodb import MongoDbRobotRepository

from .settings import MongoSettingsDep, SettingsDep


def get_user_repository(
    settings: SettingsDep, mongo_settings: MongoSettingsDep
) -> RobotRepository:
    if settings.REPOSITORY == "inmemory":
        return InMemoryRobotRepository()
    elif settings.REPOSITORY == "mongodb":
        return MongoDbRobotRepository(AsyncMongoClient(mongo_settings.HOST))
    else:
        raise NotImplementedError(f"Repository {settings.REPOSITORY} not implemented")


RepositoryDep = Annotated[RobotRepository, Depends(get_user_repository)]
