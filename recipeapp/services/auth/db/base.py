from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr


class AuthBase(AsyncAttrs, DeclarativeBase):
    """Базовая модель для auth сервиса"""
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        """ВСЕ модели auth service в схеме 'auth'"""
        return {'schema': 'auth'}
    


    

