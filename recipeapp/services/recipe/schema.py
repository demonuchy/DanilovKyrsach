from pydantic import BaseModel

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Модель для ингредиента в рецепте
class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_optional: bool = False
    preparation_note: Optional[str] = None

# Модель для тега
class RecipeTagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    slug: str
    category: Optional[str] = None
    color: Optional[str] = None

# Модель для профиля автора
class RecipeAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: Optional[str] = None
    mail: str

# Основная модель рецепта
class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Связанные данные
    profile: RecipeAuthorResponse
    ingredient_associations: List[RecipeIngredientResponse]
    tag_associations: List[RecipeTagResponse]
    favorite_count: int = 0