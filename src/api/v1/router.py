from fastapi import APIRouter

from .endpoints import robot

router = APIRouter()
router.include_router(robot.router, prefix="/robot", tags=["robot"])
