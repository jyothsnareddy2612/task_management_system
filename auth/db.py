from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth.settings import get_auth_settings


auth_settings = get_auth_settings()
auth_engine = create_async_engine(auth_settings.database_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
AuthSessionLocal = async_sessionmaker(auth_engine, expire_on_commit=False, autoflush=False)


async def get_auth_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session configured from the auth service env."""

    async with AuthSessionLocal() as session:
        yield session
