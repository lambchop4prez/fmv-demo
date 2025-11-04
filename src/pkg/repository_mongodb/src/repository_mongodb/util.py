from beanie import init_beanie
from config.mongo import settings
from pymongo import AsyncMongoClient
from repository_mongodb.models import RobotDocument


async def init_db() -> None:
    await init_beanie(
        database=AsyncMongoClient(settings.HOST).robot, document_models=[RobotDocument]
    )
