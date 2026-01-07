from pydantic import BaseModel


class RobotTask(BaseModel):
    robot: str
    task_id: str
    status: str
