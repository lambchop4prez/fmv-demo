from fastapi import APIRouter
from fastapi_oauth2.router import router as oauth2_router

from api.v1.endpoints import robot

router = APIRouter()
router.include_router(robot.router, prefix="/robot", tags=["robot"])
router.include_router(oauth2_router, tags=["oauth2"])
