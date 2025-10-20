from typing import Annotated

from beanie import Document, Indexed
from models import RobotProfile


class RobotDocument(Document, RobotProfile):
    name: Annotated[str, Indexed(str, unique=True)]
