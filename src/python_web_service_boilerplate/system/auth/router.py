from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from python_web_service_boilerplate.system.auth.schemas import AuthTokenResponse, UserRegistration
from python_web_service_boilerplate.system.auth.service import create_user
from python_web_service_boilerplate.system.auth.service import login as auth_login

router = APIRouter(prefix="/api/v1")
http_basic = HTTPBasic()


@router.post("/token")
async def login(credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)]) -> AuthTokenResponse:
    return await auth_login(credentials)


@router.post("/users")
async def register_user(user: UserRegistration) -> UserRegistration:
    return await create_user(user)
