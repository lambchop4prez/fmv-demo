from pydantic import BaseModel, Field


class Robot(BaseModel):
    name: str
    is_great: bool = Field(False)
