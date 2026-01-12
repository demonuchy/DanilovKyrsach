import asyncio
from typing import Optional, Callable
import json 
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from aio_pika.exceptions import AMQPConnectionError
from shared.config import config as cfg
from shared.rabbit.base import BaseBroker, AbstractProduser
from shared.rabbit.produser import SimpleRabbitProducer
from shared.logger.logger import logger 


class RabbitProduser(AbstractProduser):
    def __init__(self):
        super().__init__(url=cfg.RabbitUrl)
 
    async def publish(
            self, 
            message : str, 
            queue : Optional[str] = None, 
            exch_name : Optional[str] = None,  
            routing_key : Optional[str] = None, 
            exch_type : ExchangeType = ExchangeType.TOPIC,
            exch_auto_delete : bool = False
            ) -> None:
        """
        Опубликовать сообщение
        Args:
            message : сообщение
            queue : имя очереди 
            || используем либо очереть либо exchange c routing_key
            exch_name : имя Распределителя
            eouting_key : ключ 
            exch_type : тип расспределителя
            exch_auto_delete : автоудаление 
        Returns:
            None
        """
        logger.debug(f"Send message with rabbit : {message}")
        if not self.is_connect:
            raise AMQPConnectionError("Broker is not connected. Call connect() first.")
        if queue:
            await self._broker.publish(message, queue=queue)
            return
        exch = RabbitExchange(name = exch_name, auto_delete=exch_auto_delete, type=exch_type)
        await self._broker.publish(message, exchange=exch, routing_key=routing_key)


class SRabbitProduser(SimpleRabbitProducer):
    def __init__(self, url = cfg.RabbitUrl):
        super().__init__(url=url)
    
    async def publish_dict(
        self,
        message : dict, 
        rpc : bool = False, 
        timeout : Optional[int] = 10, 
        **kwargs
        ) -> dict | None:
        corutine : Optional[Callable] = None
        response : Optional[str] = None
        message = json.dumps(message)
        if rpc and timeout:
            try:
                corutine = self.publish_rpc
                response = await asyncio.wait_for(corutine(message=message, **kwargs), timeout)
            except asyncio.TimeoutError:
                logger.warn("Failed to complete the task")
                pass
        else:
            corutine = self.publish
            response = corutine(message=message, **kwargs)
        return json.loads(response)
        


produser = SRabbitProduser()
