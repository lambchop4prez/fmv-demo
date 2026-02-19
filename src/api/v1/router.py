from fastapi import APIRouter

from api.v1.endpoints import robot

router = APIRouter()
router.include_router(robot.router, prefix="/robot", tags=["robot"])
