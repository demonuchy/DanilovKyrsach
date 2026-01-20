from __future__ import annotations
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (String, DateTime, BigInteger, ForeignKey, 
                        func, Text, Numeric, UniqueConstraint)

from .base import RecipeBase


class Favorite(RecipeBase):
    """Ассоциативная таблица для связи многие-ко-многим между Profile и Recipe"""
    __tablename__ = 'favorites'

    profile_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.profiles.user_id', ondelete='CASCADE'), 
        primary_key=True, 
        nullable=False, 
        index=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.recipes.id', ondelete='CASCADE'), 
        primary_key=True, 
        nullable=False, 
        index=True
    )  

    profile: Mapped['Profile'] = relationship('Profile')
    recipe: Mapped['Recipe'] = relationship('Recipe', lazy='selectin')  
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    order_index: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Порядок рецептов в избранном"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        comment="Заметки пользователя к рецепту в избранном"
    )
    
    def __repr__(self):
        return f"<Favorite profile={self.profile_id} recipe={self.recipe_id}>"


class Profile(RecipeBase):
    __tablename__ = 'profiles'
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    mail: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    favorites: Mapped[List['Favorite']] = relationship(
        'Favorite',
        back_populates='profile',
        lazy='selectin',
        cascade="all, delete-orphan"
    ) 


class Tag(RecipeBase):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    is_system: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
class RecipeTag(RecipeBase):
    """Ассоциативная таблица для связи многие-ко-многим между Recipe и Tag"""
    __tablename__ = 'recipe_tags'

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.recipes.id', ondelete='CASCADE'), 
        primary_key=True, 
        nullable=False
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.tags.id', ondelete='CASCADE'), 
        primary_key=True, 
        nullable=False
    )

    recipe: Mapped['Recipe'] = relationship('Recipe', back_populates='tag_associations', passive_deletes=True)
    tag: Mapped['Tag'] = relationship('Tag')
    
    added_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('recipe.profiles.user_id', ondelete='SET NULL'), 
        nullable=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    order_index: Mapped[int] = mapped_column(default=0)
    
class Recipe(RecipeBase):
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.profiles.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    profile: Mapped['Profile'] = relationship('Profile')
    ingredient_associations: Mapped[List['RecipeIngredient']] = relationship(
        'RecipeIngredient',
        back_populates='recipe',
        lazy='selectin',
        cascade="all, delete-orphan",
        passive_deletes=True 
    )
    tag_associations: Mapped[List['RecipeTag']] = relationship(
        'RecipeTag',
        back_populates='recipe',
        lazy='selectin',
        cascade="all, delete-orphan", 
        passive_deletes=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Recipe id={self.id} title='{self.title}'>"


class Ingredient(RecipeBase):
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    

class RecipeIngredient(RecipeBase):
    """Ассоциативная таблица для связи многие-ко-многим между Recipe и Ingredient"""
    __tablename__ = 'recipe_ingredients'

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.recipes.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )    
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.ingredients.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )    

    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 3),
        nullable=True,
        comment="Количество ингредиента"
    )    
    unit: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Единица измерения (г, мл, шт, ст.л., ч.л. и т.д.)"
    )    
    order: Mapped[Optional[int]] = mapped_column(
        default=0,
        nullable=True,
        comment="Порядок ингредиентов в рецепте"
    )    
    preparation_note: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Способ подготовки (нарезать, натереть и т.д.)"
    )
    is_optional: Mapped[bool] = mapped_column(
        default=False,
        comment="Обязательный или опциональный ингредиент"
    )    
    group: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Группа (для соуса, маринада, украшения)"
    )    
    state: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Состояние ингредиента"
    )    
    temperature: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Температура ингредиента"
    )  
    recipe: Mapped['Recipe'] = relationship('Recipe', back_populates='ingredient_associations', passive_deletes=True)
    ingredient: Mapped['Ingredient'] = relationship('Ingredient')

    def __repr__(self):
        return f"<RecipeIngredient recipe={self.recipe_id} ingredient={self.ingredient_id}>"
    
