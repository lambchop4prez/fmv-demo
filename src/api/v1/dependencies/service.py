from typing import Annotated

from fastapi import Depends, Request
from service import RobotService

from .repository import RepositoryDep


def get_robot_service(request: Request, repository: RepositoryDep) -> RobotService:
    return RobotService(repository)


ServiceDep = Annotated[RobotService, Depends(get_robot_service)]
