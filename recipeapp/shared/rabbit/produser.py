import uuid
import asyncio
from datetime import datetime
import aio_pika
from aio_pika.pool import Pool
from typing import Optional, Dict, Any, Callable, Tuple
from ..logger.logger import logger 

class SimpleRabbitProducer:
    """Алтернативный продюссер с пулом соединений"""
    def __init__(self, url: str):
        self.url = url
        self._connection_pool : Pool[aio_pika.Connection] = Pool(lambda: aio_pika.connect_robust(self.url), max_size=10)
        self._channel_pool = None
        
    async def _create_channel_pool(self, connection) -> Pool[aio_pika.Channel]:
        if self._channel_pool is None:
            self._channel_pool = Pool(
                lambda: connection.channel(),
                max_size=10 * 10, 
            )
        return self._channel_pool

    async def publish(
        self, 
        message: str, 
        routing_key: str, 
        exch_name: str, 
        exch_type = aio_pika.ExchangeType.TOPIC
        ) -> None:
        async with self._connection_pool.acquire() as connection:
            channel_pool = await self._create_channel_pool(connection)
            async with channel_pool.acquire() as channel:
                exchange = await channel.declare_exchange(
                    exch_name,
                    exch_type,
                    durable=True  
                )
                rabbit_message = aio_pika.Message(
                    body=message.encode('utf-8'),
                    content_type='text/plain',
                )
                await exchange.publish(
                    rabbit_message,
                    routing_key=routing_key
                )

    async def publish_rpc(
        self, 
        message: str, 
        routing_key: str, 
        exch_name: str, 
        exch_type = aio_pika.ExchangeType.TOPIC
        ) -> None:
        logger.debug("запуск rpc publish")
        async with self._connection_pool.acquire() as connection:
            channel_pool = await self._create_channel_pool(connection)
            async with channel_pool.acquire() as channel:
                queue_id = str(uuid.uuid4())
                task_id = str(uuid.uuid4())
                response_queue = await channel.declare_queue(name=queue_id)
                exchange = await channel.declare_exchange(
                    exch_name,
                    exch_type,
                    durable=True  
                )
                rabbit_message = aio_pika.Message(
                    body=message.encode('utf-8'),
                    content_type='text/plain',
                    correlation_id=task_id,
                    reply_to=response_queue.name 

                )
                logger.debug("отправли сообщение")
                await exchange.publish(
                    rabbit_message,
                    routing_key=routing_key
                )
        async with response_queue.iterator() as responses:
            async for response in responses:
                if response.correlation_id == task_id:
                    logger.debug("Получили ответ")
                    await response.ack()
                    return response.body.decode()
                
    async def close(self):
        """Закрыть все соединения"""
        await self._connection_pool.close()
        if self._channel_pool:
            await self._channel_pool.close()


