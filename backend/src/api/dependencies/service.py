from typing import Annotated

from fastapi import Depends, Request
from service import RobotService

from .repository import RepositoryDep
from .settings import SettingsDep


def get_robot_service(
    request: Request, settings: SettingsDep, repository: RepositoryDep
) -> RobotService:
    return RobotService(repository)


ServiceDep = Annotated[RobotService, Depends(get_robot_service)]
