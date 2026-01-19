from faststream.rabbit import RabbitQueue, RabbitExchange, ExchangeType, RabbitBroker, RabbitMessage
import json

from depends import _get_service
from shared.config import config as cfg
from shared.logger.logger import logger

broker = RabbitBroker(url=cfg.RabbitUrl)
user_exch = RabbitExchange("user", type=ExchangeType.TOPIC, durable=True)

# Обработчик для user.create
@broker.subscriber(
    RabbitQueue(
        name="user_create_queue",  
        routing_key="user.create"
    ),
    user_exch,
)
async def handle_user_create(message: RabbitMessage):
    """Обрабатывает ТОЛЬКО user.create события"""
    try:
        service = await _get_service()
        data = json.loads(message.body.decode())
        logger.info(f"Creating profile: {data}")
        user_id = data.get("user_id")
        mail = data.get("mail")
        await service.create_profile(user_id=user_id, mail=mail)
        return json.dumps({
            "status_code": 201,
            "message": "Profile created successfully",
            "user_id": user_id
        })
    except Exception as e:
        logger.error(f"Unexcepted event: {e}")
        return json.dumps({
            "status_code": 500,
            "message": "Erorr",
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
    try:
        service = await _get_service()
        data = json.loads(message.body.decode())
        logger.info(f"Creating user: {data}")
        user_id = data.get("user_id")
        await service.delete_profile(user_id)
        return json.dumps({
            "status_code": 200,
            "message": "Profile delet successfully",
            "user_id": user_id
        })
    except:
         return json.dumps({
            "status_code": 500,
            "message": "Error",
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

