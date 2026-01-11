import asyncio
from typing import Optional
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from shared.config import config as cfg
from shared.logger.logger import logger
from shared.rabbit.base import BaseBroker, AbstractConsumer


class RabbitConsumer(AbstractConsumer):
    def __init__(self):
        super().__init__(url=cfg.RabbitUrl)
        self._consume_task = None

    async def start_consuming(self) -> None:
        """Начать потребление сообщений"""
        logger.debug("Start consuming")
        if not self.is_connect:
            await self.connect()
        if self._consume_task and not self._consume_task.done():
            return
        self._consume_task = asyncio.create_task(self._broker.start())
    
    async def stop_consuming(self) -> None:
        """Остановить потребление сообщений"""
        logger.debug("Stop consuming")
        if self._consume_task and not self._consume_task.done():
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
        if self.is_connect:
            self.disconnect()

consumer = RabbitConsumer()