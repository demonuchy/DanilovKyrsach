
from fastapi import APIRouter, status, Header, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request

from depends import ServiceDep
from shared.depends import errors
from shared.logger.logger import logger


router = APIRouter(prefix="/api/v1/recipes")


@router.post("")
async def create_recipe():
    """создать рецепт"""


@router.get("")
async def get_recipes():
    """получить рецепты по фильтрам"""


@router.get("/{recipe_id}")
async def get_recipe():
    """получить рецепт по фильтрам"""


@router.put("/{recipe_id}")
async def update_recipe():
    """Обновить рецепт"""


@router.delete("/{recipe_id}")
async def delete_recipe():
    """Удалить рецепт"""


@router.post("/{recipe_id}/favorite")
async def add_favorite():
    """Добавить в избранное"""


@router.delete("/{recipe_id}/favorite")
async def delete_favotite():
    """Удалить из избранного"""


@router.get("/{recipe_id}/favorite")
async def get_favorite():
    """Получить избранное"""
