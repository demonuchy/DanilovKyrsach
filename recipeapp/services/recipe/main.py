import uvicorn
import asyncio
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from rabbit.consumer import consumer
from rabbit.handlers import broker

from db.context import db_health_check

from shared.logger.logger import logger




@asynccontextmanager
async def lifespan(app : FastAPI):
    consumer.add_broker(broker)
    await consumer.connect()
    await consumer.start_consuming()
    logger.info("Start recipe service")
    yield
    await consumer.stop_consuming()
    await consumer.disconnect()
    logger.info("Shutdown recipe service")


app = FastAPI(lifespan=lifespan, title="Recipes service")



@app.post("/api/v1/users")
async def user():
    return  JSONResponse(
            content={"detail" : "ok"}, 
            status_code=status.HTTP_200_OK
            )


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
  

if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, host="0.0.0.0", reload=True)