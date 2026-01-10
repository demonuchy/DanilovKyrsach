from fastapi import APIRouter, status, Header, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from depends import ServiceDep
from schema import UserRegisterRequest, ServiceUserRegister, UserLoginRequest, ServiceUserLogin
from shared.depends import errors


security = HTTPBearer()


router = APIRouter(prefix="/api/v1/auth")


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
        status_code=status.HTTP_201_CREATED)


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
    access_token, refresh_token = await service.login(data)
    return JSONResponse(
        content={
            "details" : "User login", 
            "data" : {
                "access_token" : access_token,
                "refresh_token" : refresh_token,
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
    user_id = await service.authorized(access_token=access_token, ip_addres=request.client.host)
    return JSONResponse(
        headers={"X-User-Id" : str(user_id)},
        content={"details" : "The access token is valid"}, 
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