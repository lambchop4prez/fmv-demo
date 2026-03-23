from config.session import session_settings
from config.cors import cors_settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


def middleware_stack(api: FastAPI) -> None:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in cors_settings.allow_origins
        ],
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers,
    )
    api.add_middleware(
        SessionMiddleware,
        secret_key=session_settings.secret_key,
        session_cookie=session_settings.session_cookie,
        max_age=session_settings.max_age,
        same_site=session_settings.same_site,
        https_only=session_settings.https_only,
    )
