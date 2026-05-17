from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings, get_settings
from src.constants.enums import UserRole
from src.core.exceptions import AuthenticationError, PermissionDeniedError
from src.core.services.analytics_service import AnalyticsService
from src.core.services.auth_service import AuthService
from src.core.services.comment_service import CommentService
from src.core.services.notification_service import NotificationService
from src.core.services.task_service import TaskService
from src.data.clients.postgres import get_db_session
from src.data.models.postgres.user import User
from src.data.repositories.user_repository import UserRepository
from src.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> User:
    payload = decode_token(token, "access", settings)
    user = await UserRepository(session).get_by_id(UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise AuthenticationError("Authenticated user no longer exists")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDeniedError("Insufficient role permissions")
        return user

    return dependency


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(session, settings)


def get_notification_service() -> NotificationService:
    return NotificationService()


def get_task_service(
    session: AsyncSession = Depends(get_db_session),
    notifications: NotificationService = Depends(get_notification_service),
) -> TaskService:
    return TaskService(session, notifications)


def get_comment_service(
    session: AsyncSession = Depends(get_db_session),
    notifications: NotificationService = Depends(get_notification_service),
) -> CommentService:
    return CommentService(session, notifications)


def get_analytics_service(session: AsyncSession = Depends(get_db_session)) -> AnalyticsService:
    return AnalyticsService(session)


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)
