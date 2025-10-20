from fastapi import APIRouter
from pydantic import BaseModel

utilities = APIRouter()


class HealthCheckResponse(BaseModel):
    health: str = "OK"


@utilities.get("/health")
def health() -> HealthCheckResponse:
    return HealthCheckResponse()
