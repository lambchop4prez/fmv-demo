from typing import Annotated

from beanie import Document, Indexed
from models import RobotProfile, RobotTask


class RobotDocument(Document, RobotProfile):
    name: Annotated[str, Indexed(unique=True)]


class RobotTaskDocument(Document, RobotTask):
    robot: Annotated[str, Indexed()]
    task_id: Annotated[str, Indexed(unique=True)]
