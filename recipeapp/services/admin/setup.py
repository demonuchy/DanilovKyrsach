from sqladmin import Admin, ModelView
from typing import List, Type
from sqladmin import Admin

from model_view import *
from db.context import engine
from buisnes import AdminAuthenticate
from shared.config import config as cfg 


class AdminSetup:
    """Класс управления админ панелью и представлениями"""
    def __init__(self, app, engine = engine):
        self.admin = Admin(app, engine, title="Recipe app admin", base_url="/api/v1/admin", authentication_backend=AdminAuthenticate(secret_key=cfg.ADMIN_SECRET_KEY))
        self._custom_views: List[Type[ModelView]] = [
            UserAdmin,
            UserSessionAdmin,
            ProfileAdmin,
            FavoriteAdmin,
            RecipeAdmin,
            IngredientAdmin,
            TagAdmin,
            RecipTagAdmin,
            RecipeIngredientAdmin
            ]  
        self._setup_views()

    def _setup_views(self):
        """Настройка всех View для админки"""
        for view in self._custom_views:
            self.admin.add_view(view)
