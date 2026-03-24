from typing import Annotated

from fastapi import Depends, Request
from service import RobotService, UserService

from .repository import RobotRepositoryDep, UserRepositoryDep


def get_robot_service(request: Request, repository: RobotRepositoryDep) -> RobotService:
    return RobotService(repository)


RobotServiceDep = Annotated[RobotService, Depends(get_robot_service)]


def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
