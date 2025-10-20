from contextlib import asynccontextmanager
from typing import AsyncIterator, Never

from config import Settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from .util import utilities
from .v1 import router

API_ENDPOINT = "/api"
API_VERSION = Settings().API_VERSION
BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://localhost:4173",
]


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}_{route.name}"


@asynccontextmanager
async def app_init(app: FastAPI) -> AsyncIterator[Never]:
    app.include_router(router.router, prefix=f"{API_ENDPOINT}/{API_VERSION}")
    app.include_router(utilities, prefix=API_ENDPOINT, tags=["utilities"])
    yield


app = FastAPI(
    lifespan=app_init,
    openapi_url=f"{API_ENDPOINT}/{API_VERSION}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    # dependencies=[SettingsDep],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).strip("/") for origin in BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
