from beanie import init_beanie
from config.mongo import settings
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from .models import RobotDocument, UserDocument


def get_db() -> AsyncDatabase:
    return AsyncMongoClient(settings.HOST).get_database(settings.DATABASE)


async def init_db() -> None:
    await init_beanie(
        database=get_db(),
        document_models=[RobotDocument, UserDocument],
    )
