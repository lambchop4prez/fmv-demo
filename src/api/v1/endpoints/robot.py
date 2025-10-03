from typing import List

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
from models import Robot

from ...dependencies.service import ServiceDep

router = APIRouter()


@router.get("/")
async def list(
    service: ServiceDep,
) -> List[Robot]:
    return await service.list()


@router.post("/")
async def create(service: ServiceDep, user: Robot = Body(...)) -> Response:
    if user.is_great and not user.name == "Bender":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not possible"
        )
    await service.create(user)
    return Response(status_code=status.HTTP_201_CREATED)
