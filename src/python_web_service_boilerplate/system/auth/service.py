import platform
from datetime import datetime
from http import HTTPStatus

import arrow
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordBearer
from jose import jwt
from loguru import logger
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import select
from starlette.exceptions import HTTPException

from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.configuration.database_configuration import async_db_context
from python_web_service_boilerplate.system.auth.models import User
from python_web_service_boilerplate.system.auth.schemas import AuthTokenResponse, JWTPayload, UserRegistration
from python_web_service_boilerplate.system.common_models import Deleted

# Secret key for JWT
SECRET_KEY = f"SECRET_KEY:{get_module_name()}_on_{platform.node()}"
ALGORITHM = "HS256"
# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def verify_token(token: str) -> str:
    try:
        jwt_payload = JWTPayload.model_validate(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
    except Exception as e:
        logger.error(f"Token verification failed: {e}", e)
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e
    logger.info(f"Verifying JWT: {jwt_payload}")
    if jwt_payload.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Token has expired")
    username = jwt_payload.sub
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


__TYPE = "Bearer"


async def login(credentials: HTTPBasicCredentials) -> AuthTokenResponse:
    async with async_db_context() as db:
        result = await db.execute(
            select(User).where((User.username == credentials.username) & (User.deleted == Deleted.N))
        )
    user: User | None = result.scalar()
    if not user:
        logger.warning(f"User not found by username: {credentials.username}")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid username or password")
    if not pbkdf2_sha256.verify(credentials.password, user.password):
        logger.warning(f"Password is invalid: {credentials.password}")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid username or password")
    jwt_payload = JWTPayload(sub=f"{user.username}", expires_at=arrow.now("local").shift(days=1).naive)
    token = jwt.encode(claims=jwt_payload.dump(), key=SECRET_KEY, algorithm=ALGORITHM)
    return AuthTokenResponse(access_token=token, token_type=__TYPE, expires_in=86400)  # 24 hours


async def create_user(user_registration: UserRegistration) -> UserRegistration:
    async with async_db_context() as db:
        existing_user = await db.execute(
            select(User).where((User.username == user_registration.username) & (User.deleted == Deleted.N))
        )
        if existing_user.one_or_none():
            logger.warning(f"Username already exists: {user_registration.username}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username already exists")
        new_user = User(
            username=user_registration.username,
            password=pbkdf2_sha256.hash(user_registration.password),
            email=user_registration.email,
            full_name=user_registration.full_name,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"Created new user: {new_user.username}")
        return user_registration
