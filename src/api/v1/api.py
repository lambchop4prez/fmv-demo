from config.api import settings
from fastapi import FastAPI
from api.v1.middleware import middleware_stack
from api.v1.router import router

api = FastAPI(title=settings.app_name, openapi_url="/openapi.json")

middleware_stack(api)

api.include_router(router)
