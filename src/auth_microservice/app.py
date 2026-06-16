from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.logging import AccessLogMiddleware
from src.api.middleware.metrics import MetricsMiddleware, metrics_response
from src.api.middleware.request_context import RequestContextMiddleware
from src.auth_microservice.routes import auth
from src.config.settings import get_settings
from src.observability.logging.config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=f"{settings.app_name} Auth Service", version="0.1.0")

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
    app.add_middleware(RequestContextMiddleware)

    app.include_router(auth.router, prefix="/api/v1")
    app.add_api_route("/metrics", metrics_response, methods=["GET"], include_in_schema=False)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "validation_error", "message": "Invalid request", "details": exc.errors()}},
        )

    return app


app = create_app()
