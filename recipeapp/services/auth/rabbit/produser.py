from typing import Optional
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from shared.config import config as cfg
from shared.rabbit.base import BaseBroker, AbstractProduser
from shared.logger.logger import logger 


class RabbitProduser(AbstractProduser):
    def __init__(self):
        super().__init__(url=cfg.RabbitUrl)
 
    async def publish(
            self, 
            data : str, 
            queue : str, 
            exch_name : str,  
            routing_key : str, 
            exch_type : ExchangeType = ExchangeType.TOPIC,
            exch_auto_delete : bool = False
            ) -> None:
        """
        Опубликовать сообщение
        Args:
            data : сообщение
            queue : имя очереди 
            || используем либо очереть либо exchange c routing_key
            exch_name : имя Распределителя
            eouting_key : ключ 
            exch_type : тип расспределителя
            exch_auto_delete : автоудаление 
        Returns:
            None
        """
        logger.debug(f"Send message with rabbit : {data}")
        if not self.is_connect:
            raise "Нет подключения"
        if queue:
            await self._broker.publish(data, queue=queue)
            return
        exch = RabbitExchange(name = exch_name, auto_delete=exch_auto_delete, type=exch_type)
        await self._broker.publish(data, exchange=exch, routing_key=routing_key)


produser = RabbitProduser()

