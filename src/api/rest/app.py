from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.auth import AuthContextMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.logging import AccessLogMiddleware
from src.api.middleware.metrics import MetricsMiddleware, metrics_response
from src.api.middleware.request_context import RequestContextMiddleware
from src.api.rest.routes import admin, auth, comments, health, sse, tasks, websocket
from src.config.settings import get_settings
from src.observability.logging.config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(RequestContextMiddleware)

    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(tasks.router, prefix=api_prefix)
    app.include_router(comments.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)
    app.include_router(sse.router, prefix=api_prefix)
    app.include_router(websocket.router, prefix=api_prefix)
    app.add_api_route("/metrics", metrics_response, methods=["GET"], include_in_schema=False)
    return app

