from uuid import UUID
import json
from fastapi import APIRouter, Depends, status
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import AuthJWTException
from jwt import InvalidTokenError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.users.models import User
from src.apps.users.services import UserService
from src.core.exceptions import (
    AlreadyActivatedAccountException,
    DoesNotExistException,
    InvalidConfirmationTokenException,
)
from src.database.connection import get_db

email_router = APIRouter()


@email_router.get(
    "/confirm/",
    status_code=status.HTTP_200_OK,
)
async def confirm_account(
    token: str,
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
):
    try:
        email = json.loads(auth_jwt.get_raw_jwt(token)["sub"])["email"]
    except AuthJWTException:
        raise InvalidConfirmationTokenException("Invalid token")

    await user_service.activate_account(email=email, session=session)

    return {"Success": "Account activated!"}
