from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .models import  User, UserSession
from .context import session_factory

from shared.database.base import BaseRepository, BaseUnitOfWork


class UserRepository(BaseRepository[User]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model=User)


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model=UserSession)
    
    async def filter_join(self, **filters):
        stmt = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
            else: 
                raise ValueError(f"Field {key} does not exist in {self.model.__name__}")
        result = await self.session.execute(stmt.options(joinedload(self.model.user)))
        return result.scalar_one_or_none()


class AuthUow(BaseUnitOfWork):
    
    # Добавляем анннотации просто для удобства разработки 
    # IDE будет подсказывать
    user_repository : 'UserRepository'
    session_repository : 'UserSessionRepository'

    def __init__(self):
        super().__init__(session_factory=session_factory, schema="auth")
        self.add_repo("user", UserRepository)
        self.add_repo("session", UserSessionRepository)

