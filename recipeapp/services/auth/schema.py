import re
from typing import Generic, TypeVar
from pydantic import BaseModel, Field, field_validator


T=TypeVar("T")


class MailValidatorMixin(Generic[T]):
    @field_validator('mail')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.fullmatch(pattern=pattern, string=v):
            raise ValueError("Неверный формат email")
        return v


class UserRegisterRequest(BaseModel):
    mail : str = Field(...,)
    password : str = Field(...,)


class ServiceUserRegister(UserRegisterRequest):
    device_id : str = Field(...,)  
    device_name : str = Field(...,) 
    ip_addres : str = Field(...,) 


class UserLoginRequest(UserRegisterRequest):
    pass


class ServiceUserLogin(ServiceUserRegister):
    pass