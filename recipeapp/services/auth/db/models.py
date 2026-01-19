import uuid
import enum
from typing import List
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (String, DateTime, BigInteger, UUID, 
                        Enum, ForeignKey,  func, Text, Boolean, 
                        CheckConstraint, text,)


from .base import AuthBase


class User(AuthBase):
    """
    Таблица авторизации/аунтификации пользователей
    Храним данные толкько для авторизации/аунтификации
    """
    __tablename__ = "users"
   
    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    mail : Mapped[str] = mapped_column(String, unique=True, nullable=True)
    hash_password : Mapped[str] = mapped_column(String, nullable=True)

    is_active : Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_admin : Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    created_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    sessions : Mapped[List["UserSession"]] = relationship(
        "UserSession", 
        back_populates="user", 
        cascade="delete", 
        lazy="selectin"
        )

    def __repr__(self):
        return f"<User mail={self.mail}>"
    

class UserSession(AuthBase):
    """
    Таблица сессий пользователей
    Храним данные о сессиях на устройствах пользователя
    """
    __tablename__ = "user_sessions"

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    device_id : Mapped[str] = mapped_column(String, unique=True, nullable=False)
    device_name : Mapped[str] = mapped_column(String, unique=False, nullable=False)
    ip_addres : Mapped[str] = mapped_column(String, unique=False, nullable=False)
    refresh_jti : Mapped[uuid.UUID] = mapped_column(UUID, nullable=False, index=True)
    last_activity : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    is_block : Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    user_id : Mapped[int] = mapped_column(
        ForeignKey("auth.users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
        )
    
    user : Mapped["User"] = relationship(
        "User", 
        back_populates="sessions",
        lazy="joined"
        )