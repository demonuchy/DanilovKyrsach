import asyncio
from fastapi import APIRouter, status, Header, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from depends import ServiceDep
from rabbit.produser import produser
from schema import UserRegisterRequest, ServiceUserRegister, UserLoginRequest, ServiceUserLogin
from shared.depends import errors
from shared.logger.logger import logger



security = HTTPBearer()


router = APIRouter(prefix="/api/v1/auth")

@errors()
@router.get("/rebbit/test")
async def test_rabbit():
    logger.debug("начинаем обработку ...")
    response = await produser.publish_dict(rpc = True, routing_key="user.test", message={"user_id" : 1234}, exch_name="user")
    logger.debug(f"ответ : {response} - {type(response)}")
    return JSONResponse(
        content={"details" : "OK"}, 
        status_code=status.HTTP_200_OK
        )


@errors()
@router.post("/register")
async def register(
    request : Request,
    data : UserRegisterRequest, 
    service : ServiceDep,
    device_id = Header(..., alias="X-Device-Id"),
    device_name = Header(..., alias="X-Device-Name")
    ):
    """
    Регистрация  
    """
    data = ServiceUserRegister(
        device_id=device_id, 
        device_name=device_name,
        ip_addres=request.client.host,
        **data.model_dump()
        )
    access_token, refresh_token = await service.register(data)
    return JSONResponse(
        content={
            "details" : "User register", 
            "data" : {
                "access_token" : access_token,
                "refresh_token" : refresh_token,
                }
            }, 
        status_code=status.HTTP_201_CREATED
        )


@errors()
@router.post("/login")
async def login(request : Request,
    data : UserLoginRequest, 
    service : ServiceDep,
    device_id = Header(..., alias="X-Device-Id"),
    device_name = Header(..., alias="X-Device-Name")
    ):
    """
    Вход
    """
    data = ServiceUserLogin(
        device_id=device_id, 
        device_name=device_name,
        ip_addres=request.client.host,
        **data.model_dump()
        )
    access_token, refresh_token, is_admin = await service.login(data)
    return JSONResponse(
        content={
            "detail" : "User login", 
            "data" : {
                "access_token" : access_token,
                "refresh_token" : refresh_token,
                "user" : {
                    "is_admin" : is_admin
                    }
                }
            }, 
        status_code=status.HTTP_200_OK
        )


@errors()
@router.post("/authorized")
async def authorized(
    request : Request, 
    service : ServiceDep, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    """
    Верефикация access token
    """
    access_token = credentials.credentials
    user_id, is_admin = await service.authorized(access_token=access_token, ip_addres=request.client.host)
    return JSONResponse(
        headers={"X-User-Id" : str(user_id)},
        content={
            "details" : "The access token is valid", 
            "data" :{
                "user" : {
                    "is_admin" : is_admin
                }
            }
        }, 
        status_code=status.HTTP_200_OK
        )


@errors()
@router.post("/refresh")
async def authorized(
    request : Request, 
    service : ServiceDep, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    """
    Верефикация refresh токена
    """
    refresh_token = credentials.credentials
    user_id, access_token = await service.refresh(refresh_token=refresh_token, ip_addres=request.client.host)
    return JSONResponse(
        content={
            "details" : "The refresh token is valid", 
            "data" : {
                "access_token" : access_token,
                }
            }, 
        status_code=status.HTTP_200_OK
        )


@errors()
@router.post("/logout")
async def logout(
    service : ServiceDep, 
    user_id = Header(..., alias="X-User-Id"), 
    device_id = Header(..., alia="X-Device-Id"),
    ):
    await service.logout(user_id = user_id, device_id = device_id)
    return JSONResponse(
        content = {"deiail" : "Logout sucsessfull"}, 
        status_code=status.HTTP_200_OK
        )