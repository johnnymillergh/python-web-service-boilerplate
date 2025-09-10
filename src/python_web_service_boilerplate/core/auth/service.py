from datetime import datetime
from http import HTTPStatus
from typing import Final

import arrow
from advanced_alchemy import service
from fastapi.security import HTTPBasicCredentials
from jose import jwt
from loguru import logger
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import select
from starlette.exceptions import HTTPException

from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.common.profiling import elapsed_time
from python_web_service_boilerplate.common.router_loader import ALL_SCOPES
from python_web_service_boilerplate.configuration.application import pyproject_toml
from python_web_service_boilerplate.core.auth.models import User
from python_web_service_boilerplate.core.auth.repository import Repository
from python_web_service_boilerplate.core.auth.schemas import AuthTokenResponse, JWTPayload, UserRegistration
from python_web_service_boilerplate.core.common_models import Deleted

# Secret key for JWT
_SECRET_KEY = f"SECRET_KEY::{get_module_name()}::{pyproject_toml['tool']['poetry']['description']}"
_ALGORITHM = "HS256"


class UserService(service.SQLAlchemyAsyncRepositoryService[User, Repository]):
    repository_type = Repository
    __t_type: Final[str] = "Bearer"

    @staticmethod
    @elapsed_time("WARNING")
    def verify_token(token: str) -> JWTPayload:
        try:
            jwt_payload = JWTPayload.model_validate(jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM]))
        except Exception as e:
            logger.error(f"Token verification failed: {e}", e)
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED.value, detail=f"Invalid token: {e}") from e
        logger.info(f"Verifying JWT: {jwt_payload}")
        if jwt_payload.eat < datetime.now():
            logger.error(f"JWT expired: {jwt_payload}")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED.value, detail="Invalid token: expired")
        return jwt_payload

    @elapsed_time("WARNING")
    async def create_user(self, user_registration: UserRegistration) -> UserRegistration:
        existing_user = await self.get_one_or_none(
            statement=select(1).where(User.username == user_registration.username, User.deleted == Deleted.N)
        )
        if existing_user:
            logger.warning(f"Username already exists: {user_registration.username}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username already exists")
        new_user = User(
            username=user_registration.username,
            password=pbkdf2_sha256.hash(user_registration.password),
            email=user_registration.email,
            full_name=user_registration.full_name,
            scopes=",".join(user_registration.scopes) if user_registration.scopes else ",".join(ALL_SCOPES),
        )
        await self.create(new_user)
        logger.info(f"Created new user: {new_user.username}")
        return user_registration

    @elapsed_time("WARNING")
    async def login(self, credentials: HTTPBasicCredentials) -> AuthTokenResponse:
        user = await self.get_one_or_none(User.username == credentials.username)
        if not user:
            logger.warning(f"User not found by username: {credentials.username}")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED.value, detail="Invalid username or password")
        if not pbkdf2_sha256.verify(credentials.password, user.password):
            logger.warning(f"Password is invalid: {credentials.password}")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED.value, detail="Invalid username or password")
        jwt_payload = JWTPayload(sub=user.username, eat=arrow.now("local").shift(days=1).naive, scp=user.scopes)
        token = jwt.encode(claims=jwt_payload.dump(), key=_SECRET_KEY, algorithm=_ALGORITHM)
        return AuthTokenResponse(access_token=token, token_type=self.__t_type, expires_in=86400)  # 24 hours
