from typing import Annotated
from fastapi import Depends

from buisnes import AuthService
from db.repository import AuthUow


async def _get_service():
    return AuthService(
        uow_factory=AuthUow,
        )

ServiceDep = Annotated[AuthService, Depends(_get_service)]


