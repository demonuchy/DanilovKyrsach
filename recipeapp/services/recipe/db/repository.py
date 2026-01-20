from typing import List 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func, or_, and_, update, delete
from sqlalchemy.orm import joinedload, selectinload, aliased

from .models import Profile, Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag, Favorite
from .context import session_factory

from shared.database.base import BaseRepository, BaseUnitOfWork


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Profile)


class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Recipe)

    async def get_recipes_by_ingredients_with_relations_and(self, ingredient_names, tag_names):
        """
        Поиск рецептов, содержащих указанные ингредиенты и теги
        С полной загрузкой всех связанных данных
        Args:
            ingredient_names: имена ингредиентов
            tag_names: имена тегов
        Returns:
            list[obj]
        """
        stmt = select(Recipe).options(
            selectinload(Recipe.profile),
            selectinload(Recipe.ingredient_associations).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.tag_associations).selectinload(RecipeTag.tag),
        )
        if ingredient_names:
            ingredient_subquery = (
                select(RecipeIngredient.recipe_id)
                .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
                .where(or_(*[Ingredient.name.ilike(f"%{name}%") for name in ingredient_names]))
                .group_by(RecipeIngredient.recipe_id)
                .having(func.count(distinct(RecipeIngredient.ingredient_id)) >= len(ingredient_names))
            ).subquery()
            stmt = stmt.where(Recipe.id.in_(select(ingredient_subquery.c.recipe_id)))

        if tag_names:
            tag_subquery = (
                select(RecipeTag.recipe_id)
                .join(Tag, RecipeTag.tag_id == Tag.id)
                .where(or_(*[Tag.name.ilike(f"%{name}%") for name in tag_names]))
                .group_by(RecipeTag.recipe_id)
                .having(func.count(distinct(RecipeTag.tag_id)) >= len(tag_names))
            ).subquery()
            
            stmt = stmt.where(Recipe.id.in_(select(tag_subquery.c.recipe_id)))
        
        stmt = stmt.distinct()
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    
    async def get_recipes_by_ingredients_with_relations(self, ingredient_names, tag_names):
        """
        Устарел!
        Поиск рецептов, содержащих указанные ингредиенты и теги
        С полной загрузкой всех связанных данных
        Args:
            ingredient_names: имена ингредиентов
            tag_names: имена тегов
        Returns:
            list[obj]
        """
        stmt = select(Recipe).options(
            selectinload(Recipe.profile),  # Загружаем профиль
            selectinload(Recipe.ingredient_associations).selectinload(RecipeIngredient.ingredient),  # Ингредиенты
            selectinload(Recipe.tag_associations).selectinload(RecipeTag.tag),  # Теги
        )
        if ingredient_names:
            stmt = stmt.join(Recipe.ingredient_associations
            ).join(RecipeIngredient.ingredient
            ).where(or_(*[Ingredient.name.ilike(f"%{name}%") for name in ingredient_names]))
        if tag_names: 
            stmt = stmt.join(Recipe.tag_associations, full=True
            ).join(RecipeTag.tag, full=True
            ).where(or_(*[Tag.name.ilike(f"%{name}%") for name in tag_names]))
        stmt = stmt.distinct()
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_id_with_ingredients(self, id : int):
        """
        Получаем рецепт по ID со всеми ингредиентами и тегами
        Args:
            id: ID рецепта
        Returns:
            obj
        """
        stmt = select(Recipe
        ).where(self.model.id == id
        ).options(
            selectinload(Recipe.profile),
            selectinload(Recipe.ingredient_associations).selectinload(RecipeIngredient.ingredient),  
            selectinload(Recipe.tag_associations).selectinload(RecipeTag.tag), 
        ).join(Recipe.tag_associations,full=True
        ).join(RecipeTag.tag,full=True
        ).join(Recipe.ingredient_associations,full=True
        ).join(RecipeIngredient.ingredient,full=True)
        result = await self.session.execute(stmt)
        recipe = result.unique().scalar_one_or_none()
        return recipe


class RecipeTagRepository(BaseRepository[RecipeTag]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = RecipeTag)


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = RecipeIngredient)

    async def update(self, recipe_id, ingredient_id, **values):
        """
        Обновление по связному ключу
        Args:
            recipe_id: ID рецепта
            ingredient_id: ID ингрежиента
        Returns:
            ...
        """
        stmt = update(self.model
        ).where(RecipeIngredient.recipe_id == recipe_id
        ).where(RecipeIngredient.ingredient_id == ingredient_id
        ).values(**values)
        await self.session.execute(stmt)



class IngredientRepository(BaseRepository[Ingredient]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Ingredient)

   

class FavoriteRepository(BaseRepository[Favorite]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Favorite)

    async def delete(self, profile_id : int, recipe_id : int):
        """
        Удаляем по связоному ключу 
        Args:
            profile_id: ID профиля пользователя
            recipe_id: ID рецепта
        Returns:
            ...
        """
        stmt = delete(self.model
        ).where(self.model.profile_id == profile_id
        ).where(self.model.recipe_id == recipe_id)
        await self.session.execute(stmt)

    async def get_favorite_recipes(
        self,
        profile_id: int
        ) -> List[Favorite]:
        """
        Получает все избранные рецепты для указанного profile_id
        вместе с полной информацией о рецептах, их ингредиентах и тегах
        Args:
            session: Асинхронная сессия SQLAlchemy
            profile_id: ID профиля пользователя
        Returns:
            List[Favorite]: Список объектов Favorite с загруженными данными
        """
        stmt = (
            select(Favorite)
            .where(Favorite.profile_id == profile_id)
            .order_by(Favorite.order_index, Favorite.created_at.desc())
            .options(
                selectinload(Favorite.recipe).selectinload(Recipe.ingredient_associations).selectinload(RecipeIngredient.ingredient),
                selectinload(Favorite.recipe).selectinload(Recipe.tag_associations).selectinload(RecipeTag.tag),
                selectinload(Favorite.recipe).selectinload(Recipe.profile)
            )
        )
        result = await self.session.execute(stmt)
        favorites = result.scalars().all()
        return favorites



class TagRepository(BaseRepository[Tag]):
    def __init__(self, session : AsyncSession):
        super().__init__(session=session, model = Tag)
    

class RecipehUow(BaseUnitOfWork):
    
    # Добавляем анннотации просто для удобства разработки 
    # IDE будет подсказывать
    profile_repository : 'ProfileRepository'
    recipe_repository : 'RecipeRepository'
    ingredient_repository : 'IngredientRepository'
    tag_repository : 'TagRepository'
    recipe_ingredient_repository : 'RecipeIngredientRepository'
    recipe_tag_repository : 'RecipeTagRepository'
    favorite_repository :  'FavoriteRepository'

    def __init__(self):
        super().__init__(session_factory=session_factory, schema="recipe")
        self.add_repo("profile", ProfileRepository)
        self.add_repo("recipe", RecipeRepository)
        self.add_repo("recipe_ingredient", RecipeIngredientRepository)
        self.add_repo("recipe_tag", RecipeTagRepository)
        self.add_repo("ingredient", IngredientRepository)
        self.add_repo("tag", TagRepository)
        self.add_repo("favorite",FavoriteRepository)