from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager

from shared.config import config
from shared.logger.logger import logger


engine = create_async_engine(
    url=config.AsyncDataBaseUrl,
    echo = False,
    pool_size = 20,
    max_overflow=10,        
    pool_timeout=30,      
#   pool_recycle=1800,      
    pool_pre_ping=True,     
    )

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False, 
    class_=AsyncSession
    )


async def get_session():
    async with session_factory() as session:
        yield session



async def db_health_check():
    logger.debug("Тестируем подключение к бд")
    try:
        session = session_factory()
        logger.debug("Установливаем сессию")
        result = await session.execute(text("SELECT 1"))
        logger.debug("Выполняем запрос")
        return result.scalar()
    except Exception  as e:
        raise e
    finally:
        await session.aclose()
