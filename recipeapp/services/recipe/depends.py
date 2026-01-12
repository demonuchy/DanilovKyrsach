from typing import Annotated
from fastapi import Depends

from buisnes import RecipeService
from db.repository import RecipehUow


async def _get_service():
    return RecipeService(
        uow_factory=RecipehUow,
        )

ServiceDep = Annotated[RecipeService, Depends(_get_service)]