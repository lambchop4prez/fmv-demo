from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    health: str = "OK"


@router.get("/health")
def health(request: Request) -> HealthCheckResponse:
    print(request.session)
    return HealthCheckResponse()
