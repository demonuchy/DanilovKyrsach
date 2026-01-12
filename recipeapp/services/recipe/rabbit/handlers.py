from faststream.rabbit import RabbitQueue, RabbitExchange, ExchangeType, RabbitBroker, RabbitMessage
import json

from shared.config import config as cfg
from shared.logger.logger import logger

broker = RabbitBroker(url=cfg.RabbitUrl)
user_exch = RabbitExchange("user", type=ExchangeType.TOPIC, durable=True)

# Обработчик для user.create
@broker.subscriber(
    RabbitQueue(
        name="user_create_queue",  # УНИКАЛЬНОЕ имя очереди!
        routing_key="user.create"
    ),
    user_exch,
)
async def handle_user_create(message: RabbitMessage):
    """Обрабатывает ТОЛЬКО user.create события"""
    data = json.loads(message.body.decode())
    logger.info(f"Creating user: {data}")
    
    # Логика создания пользователя
    user_id = data.get("user_id")
    # ... ваша бизнес-логика ...
    
    return json.dumps({
        "status_code": 201,
        "message": "User created successfully",
        "user_id": user_id
    })

# Обработчик для user.update
@broker.subscriber(
    RabbitQueue(
        name="user_update_queue",  
        routing_key="user.update" 
    ),
    user_exch,
)
async def handle_user_update(message: RabbitMessage):
    """Обрабатывает ТОЛЬКО user.update события"""
    data = json.loads(message.body.decode())
    logger.info(f"Updating user: {data}")
    
    # Логика обновления пользователя
    user_id = data.get("user_id")
    updates = data.get("updates", {})
    # ... ваша бизнес-логика ...
    
    return json.dumps({
        "status_code": 200,
        "message": "User updated successfully",
        "user_id": user_id
    })

# Обработчик для user.delete
@broker.subscriber(
    RabbitQueue(
        name="user_delete_queue",  # 
        routing_key="user.delete"
    ),
    user_exch,

)
async def handle_user_delete(message: RabbitMessage):
    """Обрабатывает ТОЛЬКО user.delete события"""
    data = json.loads(message.body.decode())
    logger.info(f"Deleting user: {data}")
    
    # Логика удаления пользователя
    user_id = data.get("user_id")
    # ... ваша бизнес-логика ...
    
    return json.dumps({
        "status_code": 200,
        "message": "User deleted successfully",
        "user_id": user_id
    })

