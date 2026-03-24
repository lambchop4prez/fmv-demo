from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    active: Optional[bool] = False
    name: str
    sub: str
    picture: str
    email: str
    email_verified: bool
