import uuid
import enum
from typing import List
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (String, DateTime, BigInteger, UUID, 
                        Enum, ForeignKey,  func, Text, Boolean, 
                        CheckConstraint, text,)

from .base import RecipeBase


class Profile(RecipeBase):
    __tablename__ = 'user_profiles'

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id : Mapped[int] = ...
    

class Recipe(RecipeBase):
    __tablename__ = 'recipes'

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title : Mapped[str] = ...
    description : Mapped[str] = ...


class Ingredient(RecipeBase):
    __tablename__ = 'ingredients'

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name : Mapped[str] = ...


class RecipeIngredient(RecipeBase):
    __tablename__ = 'recipe_ingredients'

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    recipe_id : Mapped[int] = ...
    ingredient_id : Mapped[int] = ...

