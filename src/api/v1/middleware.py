from config.cors import get_cors_settings
from config.session import get_session_settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


def middleware_stack(api: FastAPI) -> None:
    cors = get_cors_settings()
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in cors.allow_origins],
        allow_credentials=cors.allow_credentials,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
    )
    session = get_session_settings()
    api.add_middleware(
        SessionMiddleware,
        secret_key=session.secret_key,
        session_cookie=session.session_cookie,
        max_age=session.max_age,
        same_site=session.same_site,
        https_only=session.https_only,
    )
