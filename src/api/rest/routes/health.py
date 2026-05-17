from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.clients.postgres import get_db_session
from src.data.clients.redis import get_redis
from src.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(session: AsyncSession = Depends(get_db_session)) -> HealthResponse:
    database = "ok"
    redis_status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        database = "degraded"
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        redis_status = "degraded"
    status = "ok" if database == "ok" and redis_status == "ok" else "degraded"
    return HealthResponse(status=status, database=database, redis=redis_status)


@router.get("/ready")
async def readiness() -> dict[str, str]:
    return {"status": "ready"}

