import logging
from contextlib import asynccontextmanager

from config.api import settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from repository_mongodb import init_db
from api.v1.api import api as v1


API_ENDPOINT = "/api"
API_VERSION = settings.api_version

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
    openapi_url="/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)
app.mount(f"{API_ENDPOINT}/{API_VERSION}", v1)
