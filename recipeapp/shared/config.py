import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import  ConfigDict
from pathlib import Path
from shared.logger.logger import logger

BASE_DIR = Path(__file__).parent.parent  # shared/ -> backend/
ENV_PATH = BASE_DIR/".env"


class Settings(BaseSettings):
    """Настройкт проекта"""

    DB_USER : str 
    DB_PASS : str 
    DB_HOST : str 
    DB_NAME : str
    DB_PORT : int 
    DB_CONTAINER_NAME : str

    REDIS_HOST : str
    REDIS_PORT : str
    REDIS_CONTAINER_NAME : str
    REDIS_PASSWORD : str

    JWT_SECRET_KEY : str
    JWT_ACCESS_EXPIRE_MINETS : int
    JWT_REFRESH_EXPIRE_MINETS : int
    JWT_ALGORITM : str
    JWT_KID : str

    @property
    def AsyncDataBaseUrl(self):
        """Url для подключения к базе данных"""
        if os.getenv('IN_DOCKER'):
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_CONTAINER_NAME}:{self.DB_PORT}/{self.DB_NAME}"
        return  f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DataBaseUrl(self):
        """Url для подключения к базе данных"""
        if os.getenv('IN_DOCKER'):
            return  f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_CONTAINER_NAME}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
    @property
    def RedisHost(self):
        if os.getenv('IN_DOCKER'):
            return self.REDIS_CONTAINER_NAME
        return self.REDIS_HOST
    
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False, 
        extra="ignore"
    )

config = Settings()