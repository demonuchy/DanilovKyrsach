import jwt
import time
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Literal

from shared.logger.logger import logger
from shared.config import config 


def _create_token(
        kid: str, 
        user_id: int, 
        type: Literal["access", "refresh"], 
        expire_minutes: int,
        **kwargs
        ) -> str:
    
    """
    Созданеие JWT токена 
    Args:
        kid (str): id ключа.
        user_id (int): id владельца токена.
        jti (UUID) : id токена
        type (str): тип токена access || refresh
        expire_minutes (int): время жизни токена
    Returns:
        token: JWT токен.
        jti: id токена
    """
    
    exp = datetime.now() + timedelta(minutes=expire_minutes)
    jti = uuid.uuid4()
    payload = {
        "user_id": user_id,
        "jti" : str(jti),
        "type": type,
        "exp": exp,
        "iat": datetime.utcnow()
    }
    payload.update(kwargs)
    headers = {"kid": str(kid)}
    token = jwt.encode(
        payload=payload,
        key=config.JWT_SECRET_KEY, 
        algorithm=config.JWT_ALGORITM,  
        headers=headers
    )
    return jti,  token



def create_access_token(
        user_id: int, 
        **kwargs
        ) -> str:
    
    """
    Создание access токена 
    Args:
        user_id : id пользователя
        **kwargs : дополнителные данные для pyload
    Returns:
        token: JWT токен.
        jti: id токена
    """

    jti, token = _create_token(
        kid=config.JWT_KID,
        user_id=user_id, 
        type="access", 
        expire_minutes=config.JWT_ACCESS_EXPIRE_MINETS, 
        **kwargs
        )
    return jti, token
    


def create_refresh_token(    
        user_id: int, 
        **kwargs
        ) -> str:
    
    """
    Создание refresh токена
    Args:
        user_id : id пользователя
        **kwargs : дополнителные данные для pyload
    Returns:
        token: JWT токен.
        jti: id токена
    """

    jti, token = _create_token(
        kid=config.JWT_KID,
        user_id=user_id, 
        type="refresh", 
        expire_minutes=config.JWT_REFRESH_EXPIRE_MINETS, 
        **kwargs
        )
    return jti, token


def verefy_token(
        token : str, 
        key : str = config.JWT_SECRET_KEY,
        algorithms=[config.JWT_ALGORITM]
        ) -> dict | None:
    
    """
    Валидация JWT токена
    Args:
        token : токен
        key : секретный ключ
    Returns:
        pyload : если токен валиден
    """
    
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        pyload = jwt.decode(
            jwt=token, 
            key=key, 
            algorithms=algorithms
            )
        return pyload
    except jwt.InvalidSignatureError:
        logger.warn("Подпись недействительна!")
        return None
    except jwt.ExpiredSignatureError:
        logger.warn("Токен просрочен!")
        return None
    except jwt.InvalidIssuerError:
        logger.warn("Неверный издатель токена!")
        return None
    except Exception as e:
        logger.warn(f"Ошибка проверки токена: {e}")
        raise

