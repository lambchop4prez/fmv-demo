from typing import Annotated

from fastapi import Depends
from pymongo import AsyncMongoClient
from repository import RobotRepository, UserRepository
from repository_inmemory import InMemoryRobotRepository
from repository_mongodb import MongoDbRobotRepository, MongoDbUserRepository

from .settings import MongoSettingsDep, SettingsDep


def get_robot_repository(
    settings: SettingsDep, mongo_settings: MongoSettingsDep
) -> RobotRepository:
    if settings.repository == "inmemory":
        return InMemoryRobotRepository()
    elif settings.repository == "mongodb":
        return MongoDbRobotRepository(AsyncMongoClient(mongo_settings.HOST))
    else:
        raise NotImplementedError(f"Repository {settings.repository} not implemented")


RobotRepositoryDep = Annotated[RobotRepository, Depends(get_robot_repository)]


def get_user_repository() -> UserRepository:
    return MongoDbUserRepository()


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
