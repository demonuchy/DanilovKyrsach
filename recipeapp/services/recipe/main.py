import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from shared.logger.logger import logger

@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Start recipe service")
    yield
    logger.info("Shutdown recipe service")


app = FastAPI(lifespan=lifespan)

@app.post("/api/v1/users")
async def user():
    return  JSONResponse(
            content={"detail" : "ok"}, 
            status_code=status.HTTP_200_OK
            )

@app.get("/health")
async def db_health():
    return  JSONResponse(
            content={"detail" : "Auth service the connection to the database is established"}, 
            status_code=status.HTTP_200_OK
            )
  

if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, host="0.0.0.0", reload=True)