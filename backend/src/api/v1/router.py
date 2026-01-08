from api.v1.endpoints import robot
from fastapi import APIRouter

router = APIRouter()
router.include_router(robot.router, prefix="/robot", tags=["robot"])
