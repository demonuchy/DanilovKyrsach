import abc
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Optional, TypeVar, Generic, Type, Any, Annotated, Dict, AsyncGenerator
from sqlalchemy import select, update, delete, BigInteger, func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import  DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, AsyncAttrs
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


from ..logger.logger import logger


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс модели"""
    __abstract__ = True

 
T = TypeVar('T', bound=Base)


class BaseRepository(abc.ABC, Generic[T]):

    """
    Базовый репозиторий для работы с моделями БД

    Args:
        session : сессия 
        model : модель (При наследовании)

    Example:
        Пример наследования 

        class UserRepository(BaseRepository[UserModel]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, UserModel)
            
            ...

        Использование в ендпоинтах

        @app.get("/")
        async def test(request : Request, session = Depends(get_async_session)):
            repository = UserRepository(session)
            ...
    
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    # READ operations
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по его ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить все объекты с пагинацией"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Получить объект по значению поля"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == value)
        )
        return result.scalar_one_or_none()

    async def get_many_by_field(self, field_name: str, value: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить несколько объектов по значению поля с пагинацией"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        result = await self.session.execute(
            select(self.model)
            .where(getattr(self.model, field_name) == value)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def filter(self, **filters) -> T:
        stmt = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
            else: 
                raise ValueError(f"Field {key} does not exist in {self.model.__name__}")
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # CREATE operations
    
    async def create(self, **kwargs) -> T:
        """Создать новый объект"""
        entity = self.model(**kwargs)
        self.session.add(entity)
        try:
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Entity already exists or constraint violation"
            )

    # UPDATE operations
    
    async def update(self, id: int, **kwargs) -> Optional[T]:
        """Обновить объект по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        entity = result.scalar_one_or_none()
        if not entity:
            return None 
        for field, value in kwargs.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        try:
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Update violates constraints"
            )

    async def update_by_field(self, field_name: str, field_value: Any, **kwargs) -> bool:
        """Обновить объекты по значению поля"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        stmt = (
            update(self.model)
            .where(getattr(self.model, field_name) == field_value)
            .values(**kwargs)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount > 0
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Update violates constraints"
            )

    # DELETE operations
    
    async def delete(self, id: int) -> bool:
        """Удалить объект по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        entity = result.scalar_one_or_none()
        if not entity:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def delete_by_field(self, field_name: str, value: Any) -> bool:
        """Удалить объекты по значению поля"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        stmt = delete(self.model).where(getattr(self.model, field_name) == value)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    # COUNT operations
    
    async def count(self) -> int:
        """Получить общее количество объектов"""
        result = await self.session.execute(select(self.model))
        return len(result.scalars().all())

    async def count_by_field(self, field_name: str, value: Any) -> int:
        """Получить количество объектов по значению поля"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == value)
        )
        return len(result.scalars().all())

    # EXISTS operations
    
    async def exists(self, id: int) -> bool:
        """Проверить существование объекта по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_field(self, field_name: str, value: Any) -> bool:
        """Проверить существование объекта по значению поля"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in {self.model.__name__}")
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == value)
        )
        return result.scalar_one_or_none() is not None
    

class AnnotationTypeUow(type):

    def __new__(mcs, name, bases, nameplace):
        print(f"Вызов __new__ meta")
        cls = super().__new__(mcs, name, bases, nameplace)
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = {}
        return cls
    
    def __init__(cls, name, bases, nameplace):
        print(f"Вызов __init__ meta")
        super().__init__(name, bases, nameplace)
        if "add_repository" in nameplace:
            original_add_repository = cls.add_repository
            def patch_add_repository(self, name: str, repository_cls: Type[BaseRepository]) -> None:
                result = original_add_repository(self, name, repository_cls)
                attr_name = f"{name}_repository"
                cls.__annotations__[attr_name] = repository_cls
                return result

            cls.add_repo = patch_add_repository
    

class BaseUnitOfWork(abc.ABC):
    """
    BaseUnitOfWork read/write.
    
    Args:
        session_factory: Фабрика сессий
        schema: схема (опционально)
    
    Основные изменения:
    1. Разделение read-only и write операций
    2. Автоматическое управление сессиями для read
    3. Защита от misuse (двойные транзакции и т.д.)
    
    Example:
        # Write операции (с транзакцией)
        uow = AUoW(session_factory)
        async with uow.transaction() as u:
            await u.user_repository.create(...)
        
        # Read операции (без транзакции)
        uow = AUoW(session_factory)
        async with uow.readonly() as u:
            user = await u.user_repository.get_by_id(...)
        
        # Ручное управление (для одного запроса)
        uow = AUoW(session_factory)
        repo = uow.get_repository("user")
        user = await repo.get_by_id(...)
        # Автоматическое закрытие сессии при выходе из скоупа
    """
    

    def __init__(self, session_factory: AsyncGenerator, schema: str = "public"):
        self.schema = schema
        self._session: Optional[AsyncSession] = None
        self._session_factory = session_factory
        self._repos: dict[str, Type[BaseRepository]] = {}
        self._in_transaction: bool = False
        self._session_owner: Optional[str] = None  # Кто создал сессию

    def add_repo(self, name: str, repository_cls: Type[BaseRepository]) -> None:
        """
        Регистрируем репозиторий.
        
        Args:
            name: имя репозитория (без суффикса '_repository')
            repository_cls: класс репозитория
        """
        repo_name = f"{name}_repository"
        self._repos[repo_name] = repository_cls

    def add_repository(self, name: str, repository_cls: Type[BaseRepository]) -> None:
        self.add_repo(name, repository_cls)

    def get_repository(self, name: str) -> BaseRepository:
        """
        Ручное управление: получаем репозиторий для ОДНОГО запроса.
        Сессия автоматически закрывается при уничтожении объекта.
        
        Args:
            name: имя репозитория
            
        Returns:
            Репозиторий с временной сессией
        """
        if self._session is not None:
            raise RuntimeError(
                "Сессия уже используется. Используйте readonly() или transaction() "
                "для групповых операций или создайте новый UoW."
            )
        temp_session = self._session_factory()
        repo_name = f"{name}_repository"
        repo_class = self._repos.get(repo_name)
        if not repo_class:
            raise ValueError(f"Репозиторий '{name}' не зарегистрирован")
        
        class DisposableRepository(repo_class):
            def __init__(self, session, cleanup_callback):
                super().__init__(session)
                self._cleanup_callback = cleanup_callback
            
            async def __adel__(self):
                await self._cleanup_callback()
        
        async def cleanup():
            await temp_session.aclose()
        
        return DisposableRepository(temp_session, cleanup)

    def _setup_repositories(self, session: AsyncSession) -> None:
        """Инициализирует все зарегистрированные репозитории."""
        for repo_name, repo_class in self._repos.items():
            repo_instance = repo_class(session)
            setattr(self, repo_name, repo_instance)

    def _cleanup_repositories(self) -> None:
        """Очищает репозитории из атрибутов."""
        for repo_name in self._repos.keys():
            if hasattr(self, repo_name):
                delattr(self, repo_name)

    @asynccontextmanager
    async def readonly(self) -> AsyncGenerator["BaseUnitOfWork", None]:
        """
        Контекстный менеджер для операций ТОЛЬКО чтения.
        НЕ открывает транзакцию!
        
        Usage:
            async with uow.readonly() as u:
                user = await u.user_repository.get_by_id(...)
        """
        if self._session is not None:
            raise RuntimeError("Сессия уже используется")
        self._session = self._session_factory()
        self._session_owner = "readonly"
        try:
            self._setup_repositories(self._session)
            yield self
        finally:
            self._cleanup_repositories()
            await self._session.aclose()
            self._session = None
            self._session_owner = None

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["BaseUnitOfWork", None]:
        """
        Контекстный менеджер для операций записи.
        Открывает транзакцию.
        
        Usage:
            async with uow.transaction() as u:
                await u.user_repository.create(...)
        """
        logger.debug("Открвываем транзакцию")
        if self._session is not None:
            raise RuntimeError("Сессия уже используется")
        self._session = self._session_factory()
        self._session_owner = "transaction"
        self._in_transaction = True
        try:
            self._setup_repositories(self._session)
            await self._session.begin()
            yield self
            await self._session.commit()
            logger.debug("Успешный коммит")
        except Exception:
            if self._session.in_transaction():
                await self._session.rollback()
            logger.warn("Ошибка откат транзакции")
            raise
        finally:
            logger.debug("Закрываем транзакцию")
            self._cleanup_repositories()
            self._in_transaction = False
            await self._session.aclose()
            self._session = None
            self._session_owner = None

    # Для обратной совместимости
    @asynccontextmanager
    async def begin(self) -> AsyncGenerator["BaseUnitOfWork", None]:
        """Алиас для transaction() (обратная совместимость)."""
        async with self.transaction() as uow:
            yield uow

    async def __adel__(self):
        """Автоматическое закрытие сессии при удалении объекта."""
        if self._session is not None and self._session_owner is None:
            await self._session.aclose()