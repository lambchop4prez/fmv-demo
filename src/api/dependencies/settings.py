from typing import Annotated

from fastapi import Depends, Request

from ..config.settings import Settings


def load_settings(request: Request) -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(load_settings)]
