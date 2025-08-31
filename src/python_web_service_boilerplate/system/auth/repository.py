from typing import Any

from sqlalchemy import Result, select

from python_web_service_boilerplate.configuration.database_configuration import async_db_context
from python_web_service_boilerplate.system.auth.models import User
from python_web_service_boilerplate.system.common_models import Deleted


async def get_user_by_username(username: str) -> Result[Any]:
    async with async_db_context() as db:
        return await db.execute(select(User).where((User.username == username) & (User.deleted == Deleted.N)))


async def save_user(user: User) -> User:
    async with async_db_context() as db:
        db.add(user)
        await db.commit()
        return user
