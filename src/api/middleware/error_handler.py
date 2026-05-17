import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.exceptions import AppError

logger = structlog.get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> JSONResponse:
        try:
            return await call_next(request)  # type: ignore[misc]
        except AppError as exc:
            logger.warning("application_error", code=exc.code, message=exc.message)
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": {"code": exc.code, "message": exc.message}},
            )
        except Exception as exc:
            logger.exception("unhandled_error", error=str(exc))
            return JSONResponse(
                status_code=500,
                content={"error": {"code": "internal_error", "message": "Unexpected server error"}},
            )

