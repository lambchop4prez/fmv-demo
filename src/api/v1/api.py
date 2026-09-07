from config.api import get_api_settings
from fastapi import FastAPI
from api.v1.middleware import middleware_stack
from api.v1.router import router

api = FastAPI(
    title=get_api_settings().app_name,
    openapi_url="/openapi.json",
    root_path_in_servers=True,
    root_path="/api/v1",
)

middleware_stack(api)

api.include_router(router)
