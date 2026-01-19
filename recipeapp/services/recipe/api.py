
from fastapi import APIRouter, status, Header, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request

from schema import RecipeFilterRequest
from depends import ServiceDep
from shared.depends import errors
from shared.logger.logger import logger





router = APIRouter(prefix="/api/v1/recipes")


@router.post("")
async def create_recipe():
    """создать рецепт"""


@router.get("")
async def get_recipes(ingredient_name : list, tag_name : list, service : ServiceDep):
    """получить рецепты по фильтрам"""
    recipes = await service.get_recipes_by_ingredient_name(ing_name=ingredient_name, tag_name=tag_name)
    return JSONResponse(
        content={
            "detail" : "ok", 
            "data" : {
                "recipes" : {recipes}
                }
        },
        status_code=status.HTTP_200_OK
    )


@router.get("/{recipe_id}")
async def get_recipe(recipe_id : int, service : ServiceDep):
    """получить рецепт по ID"""
    recipe = await service.get_recipe_by_id(recipe_id)
    return JSONResponse(
        content={
            "detail" : "ok", 
            "data" : {
                "recipe" : {recipe}
                }
        },
        status_code=status.HTTP_200_OK
    )


@router.put("/{recipe_id}")
async def update_recipe(recipe_id : int, ingredients : list, service : ServiceDep):
    """Обновить рецепт"""
    await service.update_recipe(recipe_id, ingredients)
    return JSONResponse(
        content={
            "detail" : "ok", 
        },
        status_code=status.HTTP_200_OK
    )


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id : int, service : ServiceDep, user_id = Header(..., alias = "X-User-Id")):
    """Удалить рецепт"""
    await service.delete_recipe(user_id, recipe_id)
    return JSONResponse(
        content={
            "detail" : "ok", 
        },
        status_code=status.HTTP_200_OK
    )


@router.post("/{recipe_id}/favorite")
async def add_favorite():
    """Добавить в избранное"""


@router.delete("/{recipe_id}/favorite")
async def delete_favotite():
    """Удалить из избранного"""


@router.get("/{recipe_id}/favorite")
async def get_favorite():
    """Получить избранное"""
