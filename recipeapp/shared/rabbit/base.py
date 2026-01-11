import abc
import asyncio
from typing import Optional
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from ..logger.logger import logger


class BaseBroker(abc.ABC):
    """
    Абстрактный базовый класс брокера
    Args:
        url : Url для подключения к rabbit
    """
    def __init__(self, url : str):
        self._broker : RabbitBroker = RabbitBroker(url = url)
        self._is_connect=False
    
    @property
    def is_connect(self):
        return self._is_connect

    @property
    def broker(self):
        return self._broker
    
    async def connect(self) -> None:
        """Подключаемся к rabbit"""
        logger.debug("Connect to rabbit")
        if self.is_connect:
            return 
        await asyncio.sleep(5)
        await self._broker.connect()
        self._is_connect = True

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

