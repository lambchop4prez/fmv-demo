from urllib.parse import urlparse

from fastapi import APIRouter, Body, HTTPException, Path, status
from models import Robot, RobotCollection

from ...dependencies.service import ServiceDep

router = APIRouter()


@router.get("/")
async def list(
    service: ServiceDep,
) -> RobotCollection:
    return RobotCollection(robots=await service.list())


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(service: ServiceDep, robot: Robot = Body(...)) -> Robot:
    if robot.is_great and not robot.name == "Bender":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not possible"
        )
    await service.create(robot)
    return robot


@router.get("/{name}")
async def find(service: ServiceDep, name: str = Path(...)) -> Robot:
    if (robot := await service.find(urlparse(name))) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return robot
