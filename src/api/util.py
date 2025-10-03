from fastapi import APIRouter

utilities = APIRouter()


@utilities.get("/health")
def health():
    return {"health": "ok"}
