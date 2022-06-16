import json
from typing import Union
from fastapi import Depends
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import MissingTokenError, InvalidHeaderError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.exceptions import InvalidCredentialsException, UserNotActiveException
from src.apps.users.models import User
from src.core.utils import get_object_by_id
from src.database.connection import get_db


async def authenticate_user(
    auth_jwt: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)
) -> User:
    auth_jwt.jwt_required()
    user = json.loads(auth_jwt.get_jwt_subject())
    user = await get_object_by_id(Table=User, id=user["id"], session=session)

    if user is None:
        raise InvalidCredentialsException("Invalid credentials provided.")
    if not user.is_active:
        raise UserNotActiveException("Account not activated. Please check your email.")
    return user


async def get_user_or_none(
    auth_jwt: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)
) -> Union[User, None]:
    try:
        auth_jwt.jwt_required()
        user = json.loads(auth_jwt.get_jwt_subject())
        user = await get_object_by_id(Table=User, id=user["id"], session=session)

        if user is None:
            raise InvalidCredentialsException("Invalid credentials provided.")

        return user
    except MissingTokenError as exc:
        return None
