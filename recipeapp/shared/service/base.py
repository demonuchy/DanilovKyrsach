import abc 
from functools import wraps
from typing import Optional, Callable, TypeVar, Generic

from ..database.base import BaseUnitOfWork


U = TypeVar('U', bound='BaseUnitOfWork')  # UnitOfWork type

class BaseUowService(abc.ABC, Generic[U]):
    """
    Абстрактный базовый класс сервиса с unit of worck
    Args:
        uow_factrory : ссылка на класс Unit of Worck
    """
    def __init__(self, uow_factory : U):
        self._uow_factory = uow_factory

    @property
    def uow(self) -> U:
        return self._uow_factory()
    
    @classmethod
    def transactional(cls, read_only: bool = False):
        """
        Декоратор для автоматического управления транзакциями.
        Создает НОВЫЙ UoW для каждого вызова метода.

        @BaseService.transactional()
        async def any_func(self, data : ServiceUserLoginRequest):
            self.uow.user_repository.create(...)
            ...
        """
        def decorator(method):
            @wraps(method)
            async def wrapper(self: 'BaseUowService', *args, **kwargs):
                uow = self._uow_factory()
                context_manager = uow.readonly if read_only else uow.transaction
                async with context_manager() as current_uow:
                    original_factory = self._uow_factory
                    self._uow_factory = lambda: current_uow
                    try:
                        return await method(self, *args, **kwargs)
                    finally:
                        self._uow_factory = original_factory
            return wrapper
        return decorator