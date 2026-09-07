from typing import Annotated

from config import ApiSettings, MongoSettings, get_api_settings, get_mongo_settings
from fastapi import Depends, Request


def load_settings(request: Request) -> ApiSettings:
    return get_api_settings()


def load_mongo_settings() -> MongoSettings:
    return get_mongo_settings()


SettingsDep = Annotated[ApiSettings, Depends(load_settings)]
MongoSettingsDep = Annotated[MongoSettings, Depends(load_mongo_settings)]
