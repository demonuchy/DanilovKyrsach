import httpx
import uuid
from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from shared.logger.logger import logger


class AdminAuthenticate(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        """Вызывается при входе в SQLAdmin"""
        logger.debug("Попытка входа администратор...")
        async with httpx.AsyncClient() as client:
            form = await request.form()
            mail = form.get("username")
            password = form.get("password")
            logger.debugP("получаем user agent")
            user_agent = request.headers.get("user-agent", "")
            if not user_agent:
                user_agent = {
                    "browser": "Unknown",
                    "device": "Unknown",
                    "os": "Unknown",
                    "user_agent": ""
                }
            logger.debug("отправляем запрос в сервис авторизации...")
            response = await client.post(
                url=f"http://127.0.0.1:8001/api/v1/auth/login",
                json={
                    'mail' : mail, 
                    'password' : password
                    },
                headers={
                    "X-Device-Id": str(uuid.uuid4()),
                    "X-Device-Name": str(user_agent)}
                )
            
        logger.debug("Парсим запрос...")
        response_data = response.json()
        if response.status_code != 200:
            logger.warn(f"Ошибка при входе {response_data['detail']}")
            return False
        if not  response_data['data']['user']['is_admin']:
            logger.warn(f"Ошибка при входе пользователь не являеться администратором")
            return False
        logger.debug("устанавливаем токее")
        request.session["access_token"] = response_data['data']['access_token']
        return True

    async def authenticate(self, request: Request) -> bool:
        """Проверяет аутентификацию для каждого запроса"""
        logger.debug("Проверяю авторизацию админ")
        token : Optional[dict] = request.session.get("access_token")
        if not token: 
            logger.warn("Ошибка токен не найден")
            return False
        logger.debug("отправляем запрос...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"http://127.0.0.1:8080/api/v1/auth/authorized",
                headers={"Authorization" : f"Bearer {token}"}
            )
        logger.debug("Парсим запрос...")
        response_data = response.json()
        if response.status_code != 200:
            logger.warn(f"Ошибка при входе {response_data['detail']}")
            return False
        if not  response_data['data']['user']['is_admin']:
            logger.warn(f"Ошибка при входе пользователь не являеться администратором")
            return False
        return True
        
    async def logout(self, request: Request) -> bool:
        """Очистка сессии при выходе"""