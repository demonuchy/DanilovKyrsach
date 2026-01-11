import re
from typing import Generic, TypeVar
from pydantic import BaseModel, Field, field_validator


T=TypeVar("T")


class MailValidatorMixin(Generic[T]):
    """Mixin для валидации почты"""
    @field_validator('mail')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.fullmatch(pattern=pattern, string=v):
            raise ValueError("Неверный формат email")
        return v


class UserRegisterRequest(BaseModel):
    """Модель запроса на регистрацию"""
    mail : str = Field(...,)
    password : str = Field(...,)


class ServiceUserRegister(UserRegisterRequest):
    """Модель для сервисного слоя с доп данными и доп валидациией"""
    device_id : str = Field(...,)  
    device_name : str = Field(...,) 
    ip_addres : str = Field(...,) 


class UserLoginRequest(UserRegisterRequest):
    """Модель запроса на вход"""
    pass


class ServiceUserLogin(ServiceUserRegister):
    """Модель для сервисного слоя с доп данными и доп валидациией"""
    pass