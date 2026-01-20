from fastapi import APIRouter, status, Header, Query
from fastapi.responses import JSONResponse
from fastapi.requests import Request


from schema import CreateRecipeRequest
from depends import ServiceDep
from shared.depends import errors
from shared.logger.logger import logger





router = APIRouter(prefix="/api/v1/recipes")


@router.post("")
async def create_recipe(data : CreateRecipeRequest, service : ServiceDep, user_id = Header(..., alias="X-User-Id")):
    """создать рецепт"""
    await service.create_recipe(user_id=user_id, **data.model_dump())
    return JSONResponse(
        content={
            "detail" : "ok", 
        },
        status_code=status.HTTP_201_CREATED
    )

@router.get("")
async def get_recipes(
    service : ServiceDep, 
    ingredient_name : list = Query(None), 
    tag_name : list = Query(None) 
    ):
    """получить рецепты по фильтрам"""
    recipes = await service.get_recipes_by_ingredient_name(ing_name=ingredient_name, tag_name=tag_name)
    return JSONResponse(
        content={
            "detail" : "ok", 
            "data" : {
                "recipes" : recipes
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
                "recipe" : recipe
                }
        },
        status_code=status.HTTP_200_OK
    )


@router.put("/{recipe_id}")
async def update_recipe(request : Request, recipe_id : int, service : ServiceDep):
    """Обновить рецепт"""
    query_params = dict(request.query_params)
    # Преобразуем значения при необходимости
    params = {}
    for key, value in query_params.items():
        # Пытаемся преобразовать в int если это число
        if value.isdigit():
            params[key] = int(value)
        else:
            params[key] = value
    await service.update_recipe(recipe_id=recipe_id, **params)
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


@router.post("/favorite/{recipe_id}")
async def add_favorite(
    service : ServiceDep, 
    recipe_id : int,
    user_id = Header(..., alias="X-User-Id")
    ):
    """Добавить в избранное"""
    await service.add_favorite(recipe_id, user_id)
    return JSONResponse(
        content={"detail" : "ok"}, 
        status_code=status.HTTP_201_CREATED
        )


@router.delete("/favorite/{recipe_id}")
async def delete_favotite(
    service : ServiceDep,
    recipe_id : int,
    user_id = Header(..., alias="X-User-Id")
    ):
    """Удалить из избранного"""
    await service.delete_favorite(recipe_id, user_id)
    return JSONResponse(
        content={"detail" : "ok"}, 
        status_code=status.HTTP_200_OK
        )


@router.get("/favorite")
async def get_favorite(
    service : ServiceDep, 
    user_id = Header(..., alias="X-User-Id")
    ):
    """Получить избранное"""
    favorites = await service.get_favorite(user_id)
    return JSONResponse(
        content={
            "detail" : "ok", 
            "data" : {
                "favorites" : favorites
                }
            }, 
        status_code=status.HTTP_200_OK
        )

