from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Extract lightweight auth context for logs without enforcing auth globally."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request.state.user_id = None
        return await call_next(request)  # type: ignore[misc]

