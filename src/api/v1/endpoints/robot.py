from typing import List

from fastapi import APIRouter, Body, HTTPException, status
from models import Robot

from ...dependencies.service import ServiceDep

router = APIRouter()


@router.get("/")
async def list(
    service: ServiceDep,
) -> List[Robot]:
    return await service.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(service: ServiceDep, robot: Robot = Body(...)) -> Robot:
    if robot.is_great and not robot.name == "Bender":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not possible"
        )
    await service.create(robot)
    return robot
