import uuid
import enum
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (String, DateTime, BigInteger, UUID, 
                        Enum, ForeignKey,  func, Text, Boolean, 
                        CheckConstraint, text, Numeric)

from .base import RecipeBase


class Profile(RecipeBase):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    recipes: Mapped[List['Recipe']] = relationship(
        'Recipe', 
        back_populates='profile',
        cascade='all, delete-orphan',
        lazy='dynamic'  
    )
    
    @property
    def recipe_count(self) -> int:
        return len(self.recipes) if self.recipes else 0


class Recipe(RecipeBase):
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ForeignKey к Profile
    profile_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Relationship к Profile (многие к одному)
    profile: Mapped['Profile'] = relationship(
        'Profile', 
        back_populates='recipes',
        lazy='joined'  # Часто нужен профиль с рецептом
    )
    
    ingredient_associations: Mapped[List['RecipeIngredient']] = relationship(
        'RecipeIngredient',
        back_populates='recipe',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    @property
    def ingredient_names(self) -> List[str]:
        return [ing.name for ing in self.ingredients]
    
    @property
    def author_name(self) -> str:
        return self.profile.name if self.profile else "Unknown"


class Ingredient(RecipeBase):
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    recipe_associations: Mapped[List['RecipeIngredient']] = relationship(
        'RecipeIngredient',
        back_populates='ingredient',
        cascade='all, delete-orphan'
    )
    
    @property
    def recipe_count(self) -> int:
        return len(self.recipes) if self.recipes else 0


class RecipeIngredient(RecipeBase):
    __tablename__ = 'recipe_ingredients'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # составной первичный ключ вместо отдельного id
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.recipes.id', ondelete='CASCADE'),
     
    )

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.ingredients.id', ondelete='CASCADE'),
     
    )
    
    recipe: Mapped['Recipe'] = relationship(
        'Recipe', 
        back_populates='ingredient_associations'
    )
    ingredient: Mapped['Ingredient'] = relationship(
        'Ingredient', 
        back_populates='recipe_associations'
    )

    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 3),  # 10 цифр, 3 после запятой
        nullable=True,
        comment="Количество ингредиента"
    )
    
    # Единица измерения
    unit: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Единица измерения (г, мл, шт, ст.л., ч.л. и т.д.)"
    )
    
    # Порядок в рецепте (для пошагового отображения)
    order: Mapped[Optional[int]] = mapped_column(
        default=0,
        nullable=True,
        comment="Порядок ингредиентов в рецепте"
    )
    
    # Дополнительные указания (нарезать кубиками, мелко порубить и т.д.)
    preparation_note: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Способ подготовки (нарезать, натереть и т.д.)"
    )

    is_optional: Mapped[bool] = mapped_column(
        default=False,
        comment="Обязательный или опциональный ингредиент"
    )
    
    # Группа ингредиентов (для соуса, маринада и т.д.)
    group: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Группа (для соуса, маринада, украшения)"
    )
    
    # Внешний вид/состояние (свежий, замороженный, сушеный)
    state: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Состояние ингредиента"
    )
    
    # Температура (комнатная, охлажденный и т.д.)
    temperature: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Температура ингредиента"
    )
    
    def __repr__(self):
        return f"<RecipeIngredient recipe={self.recipe_id} ingredient={self.ingredient_id}>"