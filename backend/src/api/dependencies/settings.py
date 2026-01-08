from typing import Annotated

from config import ApiSettings, MongoSettings
from fastapi import Depends, Request


def load_settings(request: Request) -> ApiSettings:
    return ApiSettings()


def load_mongo_settings() -> MongoSettings:
    return MongoSettings()


SettingsDep = Annotated[ApiSettings, Depends(load_settings)]
MongoSettingsDep = Annotated[MongoSettings, Depends(load_mongo_settings)]
