import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        started = time.perf_counter()
        response = await call_next(request)  # type: ignore[misc]
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "request_completed",
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            latency_ms=latency_ms,
            user_id=getattr(request.state, "user_id", None),
        )
        return response

