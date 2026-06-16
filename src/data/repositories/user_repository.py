from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none() # 0 rows:None,1 row:return object >1:error

    async def list_active(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.is_active.is_(True)).order_by(User.role.asc(), User.name.asc())
        )
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        self.session.add(user)
        #add():adds object to session tracking system..it doesn't immediately insert into DB.
        #tracking state consits of transient(only python memory),pending(still not committed),persistent(after flush/commit),detached
        await self.session.flush() #sends SQL to DB without committing transaction
        #flush is not equals to commit
        return user
    
