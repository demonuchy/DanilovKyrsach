from typing import Callable, Tuple
from fastapi import HTTPException, status

from db.repository import RecipehUow

from shared.service.base import BaseUowService
from shared.logger.logger import logger

class RecipeService(BaseUowService['RecipehUow']):
    """Бизнес логика сервиса рецептов"""
    def __init__(self, uow_factory : 'RecipehUow'):
        super().__init__(uow_factory)

    @BaseUowService.transactional()
    async def create_profile(self, user_id : int):
        logger.info("Create profile ...")
        profile = await self.uow.profile_repository.exists(id = user_id)
        if profile:
            logger.warm("Profile already exsist")
            raise HTTPException(
                detail="Profile alredy exsist", 
                status_code=status.HTTP_409_CONFLICT
            )
        profile = await self.uow.profile_repository.create(user_id=user_id)
        logger.info("Profile create")

    @BaseUowService.transactional()
    async def delete_profile(self, user_id : int):
        logger.info("Delete profile ...")
        await self.uow.profile_repository.delete(id = user_id)
        logger.info("Profile delete")


