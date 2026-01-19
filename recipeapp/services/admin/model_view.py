from sqladmin import ModelView
from auth.db.models import *
from recipe.db.models import *

class UserAdmin(ModelView, model=User):
    """User view админ панель"""
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [
        User.id,
        User.mail,
        User.is_admin
    ]


class UserSessionAdmin(ModelView, model=UserSession):
    name="Сеессия"
    name_plural="Пользовательские сессии"
    column_list = [
        UserSession.id,
        UserSession.device_name,
        UserSession.device_name,
        UserSession.ip_addres
    ]


class ProfileAdmin(ModelView, model=Profile):
    name="Профиль"
    name_plural="Профили"
    column_list = [
        Profile.id,
        Profile.mail,
        Profile.name,
    ]


class FavoriteAdmin(ModelView, model=Favorite):
    name="Избранное"
    name_plural="Избранное"
    column_list = [
        Favorite.id,
    ]


class RecipeAdmin(ModelView, model=Recipe):
    name="Рецепт"
    name_plural="Рецепты"
    column_list = [
        Recipe.id,
        Recipe.title,
    ]


class IngredientAdmin(ModelView, model=Ingredient):
    name="Ингредиент"
    name_plural="Ингредиенты"
    column_list = [
        Ingredient.id,
        Ingredient.name,
    ]


class TagAdmin(ModelView, model=Tag):
    name="Tag"
    name_plural="Tag"
    column_list=[
        Tag.id,
        Tag.name
    ]


class RecipeIngredientAdmin(ModelView, model=RecipeIngredient):
    name="Рецепт-Ингридиент"
    name_plural="Рецепт-Ингридиент"
    column_list = [
        RecipeIngredient.recipe_id,
        RecipeIngredient.ingredient_id
    ]

class RecipTagAdmin(ModelView, model=RecipeTag):
    name="Рецепт-Tag"
    name_plural="Рецепт-Tag"
    column_list = [
        RecipeTag.recipe_id,
        RecipeTag.tag_id
    ]