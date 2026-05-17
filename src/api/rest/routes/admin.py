from fastapi import APIRouter, Depends

from src.api.rest.dependencies import get_analytics_service, get_user_repository, require_roles
from src.constants.enums import UserRole
from src.core.services.analytics_service import AnalyticsService
from src.data.models.postgres.user import User
from src.data.repositories.user_repository import UserRepository
from src.schemas.auth import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics/tasks")
async def task_analytics(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, int]:
    return await analytics.task_counts_by_status()


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    users: UserRepository = Depends(get_user_repository),
) -> list[User]:
    return await users.list_active()
