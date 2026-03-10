import logging
from contextlib import asynccontextmanager

from config.api import settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.middleware import OAuth2Middleware
from starlette.middleware.cors import CORSMiddleware
from repository_mongodb import init_db

from api.util import utilities
from api.v1 import router
from api.auth import auth_callback, build_config

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
    openapi_url=f"{API_ENDPOINT}/{API_VERSION}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
    # middleware=[CORSMiddleware, OAuth2Middleware],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)
app.add_middleware(
    OAuth2Middleware, callback=auth_callback, config=build_config(settings)
)

app.include_router(router.router, prefix=f"{API_ENDPOINT}/{API_VERSION}")
app.include_router(utilities, prefix=API_ENDPOINT, tags=["utilities"])
app.include_router(oauth2_router, tags=["oauth2"])
