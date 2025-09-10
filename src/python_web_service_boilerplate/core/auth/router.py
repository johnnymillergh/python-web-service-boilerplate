from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger

from python_web_service_boilerplate.__main__ import alchemy
from python_web_service_boilerplate.core.auth.schemas import AuthTokenResponse, UserRegistration
from python_web_service_boilerplate.core.auth.service import UserService

router = APIRouter(prefix="/api/v1")
http_basic = HTTPBasic()


@router.post("/token")
async def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)],
    user_service: Annotated[UserService, Depends(alchemy.provide_service(UserService))],
) -> AuthTokenResponse:
    return await user_service.login(credentials)


@router.post("/users")
async def register_user(
    user: UserRegistration,
    user_service: Annotated[UserService, Depends(alchemy.provide_service(UserService))],
) -> UserRegistration:
    logger.info(f"User service hash: {user_service.__hash__()}")
    return await user_service.create_user(user)
