import logging
from contextlib import asynccontextmanager

from config.api import get_api_settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from repository_mongodb import init_db
from api.v1.api import api as v1
from api.v1.dependencies.auth import build_oidc_clients

API_ENDPOINT = "/api"

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    settings = get_api_settings()
    if settings.repository == "mongodb":
        await init_db()
    # One cached JWKS client per network-backed provider, built once per
    # process (defect 3). Static-key providers get no client: no network.
    # Always initialize (possibly empty) so dependencies never KeyError.
    # v1 is mounted as a sub-application: inside its routes `request.app`
    # is the mounted app, so mirror the registry onto v1's state as well.
    app.state.oidc_clients = build_oidc_clients()
    v1.state.oidc_clients = app.state.oidc_clients
    log.info("Lifespan Startup complete")
    yield
    log.info("Lifespan Shutdown complete")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}_{route.name}"


settings = get_api_settings()

app = FastAPI(
    title=settings.app_name,
    openapi_url="/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)
app.mount(f"{API_ENDPOINT}/{settings.api_version}", v1)
