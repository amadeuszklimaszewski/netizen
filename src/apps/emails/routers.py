import json
from fastapi import APIRouter, Depends, status
from fastapi_another_jwt_auth import AuthJWT
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.users.services import UserService
from src.database.connection import get_db

email_router = APIRouter()


@email_router.post(
    "/confirm/",
    status_code=status.HTTP_200_OK,
)
async def confirm_account(
    token: str,
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
):
    await user_service.activate_account(token=token, auth_jwt=auth_jwt, session=session)
    return {"Success": "Account activated!"}
