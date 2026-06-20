from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.db import get_auth_db_session
from auth.settings import get_auth_settings
from src.config.settings import Settings
from src.core.exceptions import AuthenticationError
from src.core.services.auth_service import AuthService
from src.data.models.postgres.user import User
from src.data.repositories.user_repository import UserRepository
from src.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_auth_db_session),
    settings: Settings = Depends(get_auth_settings),
) -> User:
    payload = decode_token(token, "access", settings)
    user = await UserRepository(session).get_by_id(UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise AuthenticationError("Authenticated user no longer exists")
    return user


def get_auth_service(
    session: AsyncSession = Depends(get_auth_db_session),
    settings: Settings = Depends(get_auth_settings),
) -> AuthService:
    return AuthService(session, settings)
