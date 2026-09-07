from beanie import init_beanie
from config.mongo import get_mongo_settings
from pymongo import AsyncMongoClient

from .models import RobotDocument, UserDocument


async def init_db() -> None:
    settings = get_mongo_settings()
    await init_beanie(
        database=AsyncMongoClient(settings.HOST)[settings.DATABASE],
        document_models=[RobotDocument, UserDocument],
    )
