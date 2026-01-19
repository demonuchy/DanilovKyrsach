
import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware

from db.context import db_health_check
from shared.logger.logger import logger
from shared.config import config as cfg
from setup import AdminSetup

@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Start admin service")
    yield
    logger.info("Shutdown admin service")


app = FastAPI(lifespan=lifespan, title="Admin service")


app.add_middleware(
    SessionMiddleware,
    secret_key=cfg.ADMIN_SECRET_KEY,  
    session_cookie="sqladmin_session",  
    max_age=3600 * 24, 
    https_only=True,  
    same_site="lax"
)


@app.get("/health")
async def db_health():
    try:
        result = await db_health_check()
        if result == 1:
            return  JSONResponse(
            content={"detail" : "Admin service the connection to the database is established"}, 
            status_code=status.HTTP_200_OK
            )
        logger.warn(f"Ошибка подключения к бд : {result}")
        return JSONResponse(
            content={"detail" : "Admin service the connection to the database is failed !"}, 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    except Exception as e:
        logger.warn(f"Ошибка подключения к бд {str(e)}")
        return JSONResponse(
            content={"detail" : "Admin service the connection to the database ian unforeseen event!"}, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

AdminSetup(app)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, host="0.0.0.0", reload=True)