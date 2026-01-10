from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr


class RecipeBase(AsyncAttrs, DeclarativeBase):
    """..."""
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        """ВСЕ модели auth service в схеме 'recipe'"""
        return {'schema': 'recipe'}