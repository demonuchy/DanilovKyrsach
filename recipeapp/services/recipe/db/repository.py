from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .models import Profile, Recipe, Ingredient, RecipeIngredient
from .context import session_factory

from shared.database.base import BaseRepository, BaseUnitOfWork


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Profile)


class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Recipe)


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = RecipeIngredient)


class RecipehUow(BaseUnitOfWork):
    
    # Добавляем анннотации просто для удобства разработки 
    # IDE будет подсказывать
    profile_repository : 'ProfileRepository'
    recipe_repository : 'RecipeRepository'
    recipe_ingredient_repository : 'RecipeIngredientRepository'

    def __init__(self):
        super().__init__(session_factory=session_factory, schema="auth")
        self.add_repo("profile", ProfileRepository)
        self.add_repo("recipe", RecipeRepository)
        self.add_repo("recipe_ingredient", RecipeIngredientRepository)