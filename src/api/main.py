import logging
from contextlib import asynccontextmanager

from config.api import settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from repository_mongodb import init_db
from starlette.middleware.cors import CORSMiddleware

from api.util import utilities
from api.v1 import router

API_ENDPOINT = "/api"
API_VERSION = settings.api_version
BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://localhost:4173",
]

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    if settings.repository == "mongodb":
        await init_db()
    log.info("Lifespan Startup complete")
    yield
    log.info("Lifespan Shutdown complete")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}_{route.name}"


app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{API_ENDPOINT}/{API_VERSION}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).strip("/") for origin in BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router.router, prefix=f"{API_ENDPOINT}/{API_VERSION}")
app.include_router(utilities, prefix=API_ENDPOINT, tags=["utilities"])
