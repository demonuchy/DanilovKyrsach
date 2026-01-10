import json
from datetime import timedelta
from typing import Any
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import  redis.asyncio as redis

from shared.config import config as cfg
from shared.logger.logger import logger
from shared.config import config as cgg


pool = redis.ConnectionPool(
            host=cfg.RedisHost,
            port=cfg.REDIS_PORT, 
            password=cfg.REDIS_PASSWORD, 
            db=0,
            max_connections=10,  
            decode_responses=True
            )

@asynccontextmanager
async def redis_session() -> AsyncGenerator[redis.Redis, None]:
    """
    Асинхронный контекстный менеджер для Redis сессии.
    
    Берет соединение из пула, выполняет операции, возвращает в пул.
    
    Пример:
        async with redis_session(db=0) as client:
            await client.set('key', 'value')
            result = await client.get('key')
    """
    client = redis.Redis(connection_pool=pool)
    
    try:
        logger.debug(f"Redis session started")
        yield client
    except Exception as e:
        logger.error(f"Redis session error: {e}")
        raise
    finally:
        logger.debug(f"Redis session ended")


async def accounting_token(key : str, value : dict, ttl : int = cfg.JWT_ACCESS_EXPIRE_MINETS) -> None:
    """
    Регистрация/учет токенов 
    Args:
        key : ключ 
        value : значение
        ttl : время жизни записи
    Returns:
        None
    """
    async with redis_session() as client:
        value_json = json.dumps(value)
        result = await client.setex(name=key, time=ttl, value=value_json)
        logger.debug(f"Token saved to Redis: {key}, TTL: {ttl}s")
        return bool(result)


async def get_token(key) -> dict:
    """
    Получение токена
    Args:
        key : ключ 
    Returns:
        value че сохранил то и получил
    """
    async with redis_session() as client:
        value_json = await client.get(key)
        if value_json is None:
            logger.debug(f"Token not found in Redis: {key}")
            return None
        value_dict = json.loads(value_json)
        logger.debug(f"Token retrieved from Redis: {key}")
        return value_dict
       