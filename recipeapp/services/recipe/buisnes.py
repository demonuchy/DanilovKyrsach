from typing import Callable, Tuple, Any, Optional
from fastapi import HTTPException, status

from schema import RecipeResponse, FavoriteResponse
from db.repository import RecipehUow

from shared.service.base import BaseUowService
from shared.logger.logger import logger

class RecipeService(BaseUowService['RecipehUow']):
    """Бизнес логика сервиса рецептов"""
    def __init__(self, uow_factory : 'RecipehUow'):
        super().__init__(uow_factory)

    @BaseUowService.transactional()
    async def create_profile(self, user_id : int, mail: str):
        logger.info("Create profile ...")
        profile = await self.uow.profile_repository.exists_by_field("user_id", user_id)
        if profile:
            logger.warm("Profile already exsist")
            raise HTTPException(
                detail="Profile alredy exsist", 
                status_code=status.HTTP_409_CONFLICT
            )
        profile = await self.uow.profile_repository.create(user_id=user_id, mail=mail)
        logger.info("Profile create")

    @BaseUowService.transactional()
    async def delete_profile(self, user_id : int):
        logger.info("Удаляем профиль ...")
        await self.uow.profile_repository.delete(id = user_id)
        logger.info("Профиль удален")

    @BaseUowService.transactional(read_only=True)
    async def get_recipes_by_ingredient_name(self, ing_name: list[str], tag_name: list[str]):
        logger.debug("Получаем рецепты по ingredient name && tag name") 
        recipes = await self.uow.recipe_repository.get_recipes_by_ingredients_with_relations_and(
            ingredient_names=ing_name, 
            tag_names=tag_name
        )
        if not recipes:
            logger.debug("recipes not found")
            raise HTTPException(
                detail="Recipe not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        logger.debug("Сереализуем....")
        serialize_recipes = [RecipeResponse.model_validate(recipe).model_dump() for recipe in recipes]
        logger.debug(f"Найдены рецепты: {serialize_recipes}")
        return serialize_recipes

    @BaseUowService.transactional(read_only=True)
    async def get_recipe_by_id(self, recipe_id : int) -> dict:
        logger.debug("get recipe by id")
        recipe = await self.uow.recipe_repository.get_by_id_with_ingredients(id=recipe_id)
        if not recipe:
            logger.debug("recipes not found")
            raise HTTPException(detail="Recipe not found", status_code = status.HTTP_404_NOT_FOUND)
        logger.debug(f"Рецеп найден {recipe}")
        serialize_recipe = RecipeResponse.model_validate(recipe).model_dump()
        return serialize_recipe
    
    @BaseUowService.transactional()
    async def delete_recipe(self, user_id : int, recipe_id : int):
        logger.debug(f"Delete recipe {recipe_id}")
        recipe = await self.uow.recipe_repository.filter(id = recipe_id, profile_id = int(user_id))
        if not recipe:
            logger.warn(f"Attemp delete recipe user {user_id}")
            raise HTTPException(
                detail = "Forbidden", 
                status_code=status.HTTP_403_FORBIDDEN
        )
        logger.debug("Рецепт удален")
        await self.uow.recipe_repository.delete(recipe_id)

    @BaseUowService.transactional()
    async def create_recipe(self, user_id : int, title : str, ingredients: list[dict[str, Any]], tags : Optional[list[dict[str, Any]]]):
        logger.debug("Cоздаем рецепт")
        recipe = await self.uow.recipe_repository.create(profile_id = int(user_id), title=title)
        logger.debug("Создаем связь с ингридиентами")
        for ingredient in ingredients:
            current_ingredient = await self.uow.ingredient_repository.get_by_field("name", ingredient.pop("name").lower())
            if not current_ingredient:
                logger.warn("ингрдиент не найден")
                raise HTTPException(detail="Ingredient not exsist", status_code=status.HTTP_404_NOT_FOUND)
            await self.uow.recipe_ingredient_repository.create(recipe_id=recipe.id, ingredient_id=current_ingredient.id, **ingredient)
        logger.debug("Добавляем теги")
        if tags:
            for tag in tags:
                current_tag = await self.uow.tag_repository.get_by_field("name", tag.pop("name").lower())
                if not current_tag:
                    logger.warn("Tag не найден")
                    raise HTTPException(detail="Tag not exsist", status_code=status.HTTP_404_NOT_FOUND)
                await self.uow.recipe_tag_repository.create(recipe_id=recipe.id, tag_id=current_tag.id)
            logger.debug("Теги добавлены")
        logger.debug("Рецепт создан")

    @BaseUowService.transactional()
    async def update_recipe(self, recipe_id: int, ingredient_id : list[int], **values):
        logger.debug(f"Обновление рецепта {recipe_id}")
        await self.uow.recipe_ingredient_repository.update(recipe_id=int(recipe_id), ingredient_id=int(ingredient_id), **values)
        logger.debug("Рецепт обновлен")

    @BaseUowService.transactional()
    async def add_favorite(self, recipe_id : int , user_id : int):
        user_id = int(user_id)
        recipe_id = int(recipe_id)
        logger.debug(f"Добавление рецепта в избранное {recipe_id}")
        favorite = await self.uow.favorite_repository.filter(profile_id = user_id, recipe_id = recipe_id)
        if favorite: 
            logger.warn("Рецепт уже в избранном")
            raise HTTPException(
                detail="Recipe already added", 
                status_code=status.HTTP_409_CONFLICT
            )
        await self.uow.favorite_repository.create(profile_id = user_id, recipe_id = recipe_id)
        logger.debug("Рецепт добаылен в избранное")

    @BaseUowService.transactional()
    async def delete_favorite(self, recipe_id : int , user_id):
        logger.debug(f"Удаление рецепта из избранного {recipe_id}")
        await self.uow.favorite_repository.delete(profile_id = int(user_id), recipe_id = int(recipe_id))
        logger.debug("рецепт удален")

    @BaseUowService.transactional()
    async def get_favorite(self, user_id : int):
        logger.debug(f"Получение избранного")
        favorites = await self.uow.favorite_repository.get_favorite_recipes(profile_id=int(user_id))
        logger.debug("сериализуем ...")
        serialize_favorites = [FavoriteResponse.model_validate(favorite).model_dump() for favorite in favorites]
        logger.debug(f"получили рецепты {serialize_favorites}")
        return serialize_favorites
       


        
