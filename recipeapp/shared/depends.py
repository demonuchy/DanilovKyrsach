from functools import wraps
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from .logger.logger import logger


def errors():
    """Обработка ошибок в ендпоинтах"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                logger.warn(f"Ошибка обработки запроса {e}")
                return JSONResponse({"details" : e.detail}, status_code=e.status_code)
            except Exception as e:
                logger.warn(f"Ошибка обработки запроса {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail=f"error: {str(e)}"
                )
        return wrapper
    return decorator