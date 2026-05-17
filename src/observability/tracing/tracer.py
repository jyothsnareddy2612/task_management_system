from contextlib import asynccontextmanager
from collections.abc import AsyncIterator


@asynccontextmanager
async def trace_span(name: str) -> AsyncIterator[None]:
    """Placeholder span boundary for future OpenTelemetry integration."""

    _ = name
    yield

