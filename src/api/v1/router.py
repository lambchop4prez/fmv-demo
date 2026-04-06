from fastapi import APIRouter

from api.v1.endpoints import auth, robot, user, util

router = APIRouter()

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    robot.router,
    prefix="/robot",
    tags=["robot"],
)

router.include_router(user.router, prefix="/user", tags=["user"])

router.include_router(util.router, tags=["util"])
