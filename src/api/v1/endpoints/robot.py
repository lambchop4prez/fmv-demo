from fastapi import APIRouter, Body, HTTPException, status
from models import RobotCollection, RobotProfile, RobotTask

from api.dependencies.service import RobotServiceDep

router = APIRouter()


@router.get("/")
async def list(service: RobotServiceDep) -> RobotCollection:
    return RobotCollection(robots=await service.list())


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
    service: RobotServiceDep, robot: RobotProfile = Body(...)
) -> RobotProfile:
    if robot.is_great and not robot.name == "Bender":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not possible"
        )
    await service.create(robot)
    return robot


@router.get("/{name}")
async def find(service: RobotServiceDep, name: str) -> RobotProfile:
    if (robot := await service.find(name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return robot


@router.post("/{name}/run")
async def run(service: RobotServiceDep, name: str) -> RobotTask:
    if (robot := await service.find(name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task = await service.start(robot)
    return task
