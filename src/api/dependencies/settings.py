from typing import Annotated

from fastapi import Depends, Request

from ..config.mongo_settings import MongoSettings
from ..config.settings import Settings


def load_settings(request: Request) -> Settings:
    return Settings()


def load_mongo_settings() -> MongoSettings:
    return MongoSettings()


SettingsDep = Annotated[Settings, Depends(load_settings)]
MongoSettingsDep = Annotated[MongoSettings, Depends(load_mongo_settings)]
