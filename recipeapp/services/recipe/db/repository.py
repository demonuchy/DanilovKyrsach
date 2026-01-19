from typing import List 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func, or_
from sqlalchemy.orm import joinedload, selectinload, aliased

from .models import Profile, Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag
from .context import session_factory

from shared.database.base import BaseRepository, BaseUnitOfWork


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Profile)


class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Recipe)
        self._stmt = None
    
    @property
    def stmt(self):
        return self._stmt
    
    def _filter_by_any_ingredient_names(self, names: List[str]):
        """Фильтр по названиям ингредиентов (достаточно ЛЮБОГО)"""
        if not names:
            return self
        subq = select(RecipeIngredient.recipe_id).join(
            Ingredient, RecipeIngredient.ingredient_id == Ingredient.id
        ).where(
            or_(*[Ingredient.name.ilike(f"%{name}%") for name in names])
        ).distinct().subquery()
        return aliased(subq, name="ing_any_filter")
    
    def _filter_by_ingredient_names(self, names: List[str]):
        """Фильтр по названиям ингредиентов (должны быть ВСЕ)"""
        if not names:
            return self
        subq = select(RecipeIngredient.recipe_id).join(
            Ingredient, RecipeIngredient.ingredient_id == Ingredient.id
        ).where(
            or_(*[Ingredient.name.ilike(f"%{name}%") for name in names])
        ).group_by(
            RecipeIngredient.recipe_id
        ).having(
            func.count(distinct(Ingredient.id)) == len(names)
        ).subquery()
        return aliased(subq, name="ing_filter")

    
    def _filter_by_any_tag_names(self, names: List[str]):
        """Фильтр по названиям тегов (достаточно ЛЮБОГО)"""
        if not names:
            return self
        subq = select(RecipeTag.recipe_id).join(
            Tag, RecipeTag.tag_id == Tag.id
        ).where(
            or_(*[Tag.name.ilike(f"%{name}%") for name in names])
        ).distinct().subquery()
        return aliased(subq, name="tag_any_filter")

    def _filter_by_tag_names(self, names: List[str]):
        """Фильтр по названиям тегов (должны быть ВСЕ)"""
        if not names:
            return self
        subq = select(RecipeTag.recipe_id).join(
            Tag, RecipeTag.tag_id == Tag.id
        ).where(
            or_(*[Tag.name.ilike(f"%{name}%") for name in names])
        ).group_by(
            RecipeTag.recipe_id
        ).having(
            func.count(distinct(Tag.id)) == len(names)
        ).subquery()
        return aliased(subq, name="tag_filter")
    
    def _paginate(self, limit: int = 50, offset: int = 0):
        """Добавить пагинацию"""
        self._stmt = self._stmt.limit(limit).offset(offset)
        return self

    async def get_recipes_by_ingredients_with_relations(self, ingredient_names, tag_names):
        """
        Поиск рецептов, содержащих указанные ингредиенты и теги
        С полной загрузкой всех связанных данных
        """
        stmt = select(Recipe).options(
            selectinload(Recipe.profile),
            selectinload(Recipe.ingredient_associations).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.tag_associations).selectinload(RecipeTag.tag),
            selectinload(Recipe.favorites)
        )
        if ingredient_names:
            stmt = stmt.join(
                Recipe.ingredient_associations
            ).join(
                RecipeIngredient.ingredient
            ).where(
                or_(*[Ingredient.name.ilike(f"%{name}%") for name in ingredient_names])
            )
        if tag_names:
            stmt = stmt.join(
                Recipe.tag_associations
            ).join(
                RecipeTag.tag
            ).where(
                or_(*[Tag.name.ilike(f"%{name}%") for name in tag_names])
            )
        stmt = stmt.distinct()
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id_with_ingredients(self, id : int):
        stmt = select(Recipe).where(Recipe.id == id).options(
            joinedload(Recipe.profile),
            selectinload(
                Recipe.ingredient_associations
            ).joinedload(
                RecipeIngredient.ingredient
            ),
            selectinload(
                Recipe.tag_associations
            ).joinedload(
                RecipeTag.tag
            )
        )
        result = await self.session.execute(stmt)
        recipe = result.unique().scalar_one_or_none()
        return recipe

class RecipeTagRepository(BaseRepository[RecipeTag]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = RecipeTag)


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = RecipeIngredient)
    
    async def update_or_create(self, recipe_id : int, ingredient : dict):
        name = ingredient["name"]
        res = await self.filter(id=recipe_id, **ingredient)
        if not res:
            res = await self.create(**ingredient)
        res = await self.update(res.id, **ingredient)
        return res


class RecipehUow(BaseUnitOfWork):
    
    # Добавляем анннотации просто для удобства разработки 
    # IDE будет подсказывать
    profile_repository : 'ProfileRepository'
    recipe_repository : 'RecipeRepository'
    recipe_ingredient_repository : 'RecipeIngredientRepository'
    recipe_tag_repository : 'RecipeTagRepository'

    def __init__(self):
        super().__init__(session_factory=session_factory, schema="auth")
        self.add_repo("profile", ProfileRepository)
        self.add_repo("recipe", RecipeRepository)
        self.add_repo("recipe_ingredient", RecipeIngredientRepository)
        self.add_repo("recipe_tag", RecipeTagRepository)