from typing import Callable, Tuple
from fastapi import HTTPException, status

from schema import ServiceUserRegister, ServiceUserLogin
from db.repository import AuthUow
from rd.context import accounting_token, get_token
from rabbit.produser import produser 
from utils.jwt_manager import create_access_token, create_refresh_token, verefy_token
from utils.password_hash import hash_password, is_password_valid
from shared.service.base import BaseUowService
from shared.logger.logger import logger

class AuthService(BaseUowService['AuthUow']):
    """Бизнес логика сервиса авторизации"""

    def __init__(self, uow_factory : 'AuthUow'):
        super().__init__(uow_factory)


    def _get_token_pair(self, user_id, device_id, mail) -> Tuple[str, str, str, str]:
        access_jti, access_token = create_access_token(user_id=user_id, device_id=device_id, mail=mail)
        refresh_jti, refresh_token = create_refresh_token(user_id=user_id, device_id=device_id, mail=mail)
        return access_jti, access_token, refresh_jti, refresh_token

    async def _accounting_token(self, user_id : int, device_id : int, access_jti : str) -> None:
        key = f"{device_id}:{user_id}"
        await accounting_token(key=key, value={"jti" : str(access_jti)})
        
    @BaseUowService.transactional()
    async def register(self, data : ServiceUserRegister) -> Tuple[str, str]: 
        """
        # Регистрация
        #### 1 проверка существования пользователя
        #### 2 создание пользователя 
        #### 3 создание токенов доступа 
        #### 4 создание сессии
        #### 5 выдача токенов
        """
        logger.info(f"Register attemp {data.mail} - {data.password}")
        logger.debug("checking if the user exists")
        user = await self.uow.user_repository.exists_by_field("mail", data.mail)
        if user:
            logger.warn(f"User already exists {data.mail} - {data.password}")
            raise HTTPException(
                detail="User already exists", 
                status_code=status.HTTP_409_CONFLICT
            )
        logger.debug("Create user ...")
        hashed_password = hash_password(data.password)
        user = await self.uow.user_repository.create(mail=data.mail, hash_password=hashed_password)
        logger.debug("Create profile ...")
        response = await produser.publish_dict(
            rpc=True, 
            routing_key="user.create", 
            message={"user_id" : user.id}, 
            exch_name="user",
            timeout=1
            )
        if not response or response['status_code'] != 201:
            logger.warn("Recipe service is not responding ")
            raise HTTPException(
                detail="Error on recipe service : failid create profile", 
                status_code=status.HTTP_502_BAD_GATEWAY
                )
        logger.debug("profile create succsesfull")
        logger.debug("Create tokens ...")
        access_jti, access_token, refresh_jti, refresh_token = self._get_token_pair(
            user_id=user.id, 
            device_id=data.device_id, 
            mail=user.mail
        )
        logger.debug("Create user session ...")
        user_session = await self.uow.session_repository.create(
            device_id = data.device_id,
            device_name = data.device_name,
            ip_addres = data.ip_addres,
            refresh_jti = refresh_jti,
            user_id = user.id
        )
        logger.debug("Save access token into redis ...")
        await self._accounting_token(user_id = user.id, device_id = data.device_id, access_jti = access_jti)
        logger.info(f"User created {data.mail} - {data.password}")
        return access_token, refresh_token
        
        
    @BaseUowService.transactional()
    async def login(self, data : ServiceUserLogin) -> Tuple[str, str]: 
        """
        # Вход
        #### 1 проверка существования пользователя 
        #### 2 сверка пароля
        #### 3 создание токенов 
        #### 4 проверка существования сессии
        #### 5 проверка активности сессии
        #### 6 обновление сессии
        #### 7 выдча токенов
        """
        logger.info(f"Login attemp {data.mail} - {data.password}")
        logger.debug("checking if the user exists")
        user = await self.uow.user_repository.get_by_field("mail", data.mail)
        if not user or not is_password_valid(data.password, user.hash_password):
            logger.warn("Unauthorized")
            raise HTTPException(
                detail="Invalid credentials" , 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        logger.debug("Create tokens ...")
        access_jti, access_token, refresh_jti, refresh_token = self._get_token_pair(
            user_id=user.id, 
            device_id=data.device_id, 
            mail=user.mail
        )
        logger.debug("checking if the session exists")
        current_session = await self.uow.session_repository.filter(user_id = user.id, device_id = data.device_id)
        if not current_session:
            logger.debug(f"Session not found, create new ...")
            """

            отправить уведомление пользователю о новом устройстве

            """ 
            current_session = await self.uow.session_repository.create(
                device_id = data.device_id,
                device_name = data.device_name,
                ip_addres = data.ip_addres,
                refresh_jti = refresh_jti,
                user_id = user.id
                )
        else:
            logger.debug(f"Session found, update ...")
            if current_session.is_block:
                logger.warn(f"Session is blocked : {data.ip_addres} - {data.device_id} - {data.mail}")
                raise HTTPException(detail="Session is blocked", status_code=status.HTTP_423_LOCKED)
            await self.uow.session_repository.update(id=current_session.id, refresh_jti=refresh_jti, ip_addres=data.ip_addres)
        logger.debug("Save access token into redis ...")
        await self._accounting_token(user_id = user.id, device_id = data.device_id, access_jti = access_jti)
        logger.info(f"User login {data.mail} - {data.password}")
        return access_token, refresh_token

    async def authorized(self, access_token : str, ip_addres : str) -> int: 
        """
        # Проверка access токена 
        #### 1 проверем подпись токена 
        #### 2 проверяем реггистрацию токена
        #### 3 возвращаем ответ 
        """
        logger.debug("Vrerefy access token")
        logger.debug(f"{access_token}")
        logger.debug("Validate token ...")
        pyload : dict = verefy_token(token=access_token)
        if not pyload:
            logger.warn("Token is not valid")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        logger.debug("Check register access token...")
        device_id = pyload.get('device_id')
        user_id = pyload.get('user_id')
        value : dict = await get_token(f"{device_id}:{user_id}")
        if not value:
            logger.warn("Token is not accouting")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        if value.get('jti') != pyload.get('jti'):
            logger.warn("Failed comparison JTI")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        logger.debug("User authenticate succsesfull")
        # проинуть в фоновую задачу обновление активности сессии
        return user_id

    @BaseUowService.transactional(read_only=True)
    async def refresh(self, refresh_token : str, ip_addres) -> int: 
        """
        # Проверка refresh
        #### 1 ПРоверяем подпись 
        #### 2 проврякм регистрацию токена 
        #### 3 создаем и регестрируем новый accsess
        #### 4 отдаем access
        """
        logger.debug("Vrerefy refresh token")
        logger.debug("Validate token ...")
        pyload : dict = verefy_token(token=refresh_token)
        if not pyload:
            logger.warn("Token is not valid")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        logger.debug("Check register refresh token...")
        device_id = pyload.get('device_id')
        user_id = pyload.get('user_id')
        current_session = await self.uow.session_repository.filter_join(device_id=device_id, user_id=user_id)
        if not current_session:
            logger.warn("Token is not accouting")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        if pyload.get("jti") != str(current_session.refresh_jti):
            logger.debug(f"|{pyload.get('jti')}| - |{current_session.refresh_jti}|")
            logger.warn("Failed comparison JTI")
            raise HTTPException(detail="Token is not valid", status_code=status.HTTP_401_UNAUTHORIZED)
        logger.debug("Accounting token...")
        access_jti, access_token = create_access_token(
            user_id=user_id, 
            device_id=current_session.device_id, 
            mail=current_session.user.mail
            )
        await self._accounting_token(user_id = user_id, device_id = device_id, access_jti = access_jti)
        logger.info("Refresh succsess")
        return user_id, access_token 
    
    async def recover_password(self, data) -> None: 
        pass

        