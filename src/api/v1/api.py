from config.api import settings
from fastapi import FastAPI
from api.v1.middleware import middleware_stack
from api.v1.router import router

api = FastAPI(
    title=settings.app_name,
    openapi_url="/openapi.json",
    root_path_in_servers="/api/v1",
    root_path="/api/v1",
)

middleware_stack(api)

api.include_router(router)
