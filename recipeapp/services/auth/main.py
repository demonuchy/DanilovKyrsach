
import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api import router
from rabbit.produser import produser
from db.context import db_health_check
from shared.logger.logger import logger


"""
Итак сервис авторизации аунтификации кратко расскажу как он работает и зачем это надо 
данный сервис как не трудно отвечает за аунтификацию и авторизацию то есть кто перед намми и можно ли ему дергать за ендпоинты в 
других сервисах

Основная технология механиз называйте как хотите - JWT  
В общих чертах пользователь в каждом запросе отправлляет access token 
если он валиден пропускаем если нет то пользователь отправляет refresh что бы получить новый access если и refresh не валиден 
то вход в аккаун по новой  (видимо у разработчиков еду дгту сессия живет 5 минут ... ну не подумали ребята) 

Таблички в бд их тут всего две 
User - хранит учетные данные почту пароль и метаданные активен ли пользователь и тд
UserSession - хранит сессию на конкретном устройстве эта табличка нужна для болеее гибкого управления аккаунта мы можем заблокировать 
не пользователя глобально а какое либо устройство  

По основным функциям можно почитать в api.py 
"""

@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Start auth service")
    yield
    logger.info("Shutdown auth service")


app = FastAPI(lifespan=lifespan, title="Auth service")


@app.get("/health")
async def db_health():
    try:
        result = await db_health_check()
        if result == 1:
            return  JSONResponse(
            content={"detail" : "Auth service the connection to the database is established"}, 
            status_code=status.HTTP_200_OK
            )
        logger.warn(f"Ошибка подключения к бд : {result}")
        return JSONResponse(
            content={"detail" : "Auth service the connection to the database is failed !"}, 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    except Exception as e:
        logger.warn(f"Ошибка подключения к бд {str(e)}")
        return JSONResponse(
            content={"detail" : "Auth service the connection to the database ian unforeseen event!"}, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, host="0.0.0.0", reload=True)