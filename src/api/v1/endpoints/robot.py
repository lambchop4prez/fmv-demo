"""Robot endpoints, protected by session auth plus scopes (deny by default).

The router-level ``get_current_user`` dependency rejects every request
without a session user (HTTP 401); each route then enforces its operation
scope from the session (HTTP 403 when missing, decision D3). Bearer tokens
are not consumed here: they are exchanged for the session cookie at
``POST /auth/login`` (decision D1=a).
"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from models import RobotCollection, RobotProfile, RobotTask

from api.v1.dependencies.session import get_current_user, require_scope
from api.v1.dependencies.service import RobotServiceDep
from api.v1.scopes import ROBOT_READ, ROBOT_RUN, ROBOT_WRITE

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", dependencies=[Depends(require_scope(ROBOT_READ))])
async def list(
    service: RobotServiceDep,
) -> RobotCollection:
    return RobotCollection(robots=await service.list())


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_scope(ROBOT_WRITE))],
)
async def create(
    service: RobotServiceDep, robot: RobotProfile = Body(...)
) -> RobotProfile:
    if robot.is_great and not robot.name == "Bender":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not possible"
        )
    await service.create(robot)
    return robot


@router.get("/{name}", dependencies=[Depends(require_scope(ROBOT_READ))])
async def find(service: RobotServiceDep, name: str) -> RobotProfile:
    if (robot := await service.find(name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return robot


@router.post("/{name}/run", dependencies=[Depends(require_scope(ROBOT_RUN))])
async def run(
    service: RobotServiceDep,
    name: str,
) -> RobotTask:
    if (robot := await service.find(name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task = await service.start(robot)
    return task
