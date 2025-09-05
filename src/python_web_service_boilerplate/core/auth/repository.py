from sqlalchemy import ScalarResult
from sqlmodel import select

from python_web_service_boilerplate.configuration.database import async_db_context
from python_web_service_boilerplate.core.auth.models import User
from python_web_service_boilerplate.core.common_models import Deleted


async def get_user_by_username(username: str) -> ScalarResult[User]:
    async with async_db_context() as db:
        return await db.exec(select(User).where(User.username == username, User.deleted == Deleted.N))


async def save_user(user: User) -> User:
    async with async_db_context() as db:
        db.add(user)
        await db.commit()
        return user
