from pydantic import BaseModel
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

## recipe/schema.py или где у вас схемы
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class IngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ingredient: IngredientResponse
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_optional: bool = False


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: Optional[str] = None
    

class RecipeTagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tag: TagResponse


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: Optional[str] = None
    mail: str


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    profile_id: int
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse
    ingredient_associations: List[RecipeIngredientResponse]
    tag_associations: List[RecipeTagResponse]

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

class CreateRecipeRequest(BaseModel):
    title : str
    ingredients: list[dict[str, Any]]
    tags : Optional[list[dict[str, Any]]] = None