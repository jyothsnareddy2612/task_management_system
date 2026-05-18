from contextvars import ContextVar
#ContextVar provides:coroutine-local storage
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware #starlette mw abstraction
from starlette.requests import Request
from starlette.responses import Response

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        request_id_ctx.set(request_id)
        request.state.request_id = request_id
        response = await call_next(request)  # continues mw chain
        response.headers["x-request-id"] = request_id
        return response

