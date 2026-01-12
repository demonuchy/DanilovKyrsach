import abc
import asyncio
import aio_pika
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, List
from aio_pika.exceptions import AMQPConnectionError
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from ..logger.logger import logger


class BaseBroker(abc.ABC):
    """
    Абстрактный базовый класс брокера
    Args:
        url : Url для подключения к rabbit
    """
    MAX_CONNECTION_ATTEMP : int 

    def __init__(self, url : str, max_connection_attemp = 5):
        self._broker : RabbitBroker = None 
        self.MAX_CONNECTION_ATTEMP = max_connection_attemp
        self._is_connect=False
        self._connection_attemp = 0
    
    @property
    def is_connect(self):
        return self._is_connect

    @property
    def broker(self):
        return self._broker
    
    async def connect(self) -> bool | None:
        """Подключаемся к rabbit"""
        try:
            logger.debug("Connect to rabbit")
            if self.broker is None:
                logger.error("Broker not found")
                raise ValueError("Broker not found")
            self._connection_attemp+=1
            if self.is_connect:
                logger.warn("Connect already exsist")
                return self.is_connect
            await self._broker.connect()
            self._is_connect = True
            logger.debug("Connect to rabbit sucsesfull")
            return self.is_connect
        except AMQPConnectionError as e:
            logger.warn("Error connect to rabitt")
            if not self.is_connect and self._connection_attemp < self.MAX_CONNECTION_ATTEMP:
                logger.warn(f"Connection attemp {self._connection_attemp}")
                await asyncio.sleep(self._connection_attemp*4)
                await self.connect()
                return
            logger.error("не удалось подключиться к rabbit")
            raise e
            
    async def disconnect(self) -> None:
        """Отключаемся от rabbit"""
        logger.debug("Disconect to rabbit")
        if not self.is_connect:
            return
        await self._broker.stop()
        self._is_connect = False


class AbstractProduser(BaseBroker, abc.ABC):
    """
    Абстрактный класс продюсера
    Args:
        url : Url для подключения к rabbit
    """
    def __init__(self, url : str):
        super().__init__(url=url)

    @abc.abstractmethod
    async def publish(self,**kwargs):
        """реализация метода отправки сообщения"""
        pass


class AbstractConsumer(BaseBroker, abc.ABC):
    """
    Абстрактный класс консьюмера
    Args:
        url : Url для подключения к rabbit
    """
    def __init__(self, url : str):
        super().__init__(url=url)

    @abc.abstractmethod
    async def start_consuming(self, **kwargs):
        """реализация метода начала прослушки"""
        pass

    @abc.abstractmethod
    async def stop_consuming(self, **kwargs):
        """реализация метода остановки прослушки"""
        pass



