from uuid import UUID
from fastapi import BackgroundTasks, Depends, status
from fastapi.routing import APIRouter
from fastapi_another_jwt_auth import AuthJWT

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.users.models import (
    FriendOutputSchema,
    FriendRequestOutputSchema,
    User,
    UserOutputSchema,
    LoginSchema,
    RegisterSchema,
)
from src.apps.users.services import UserService
from src.apps.jwt.schemas import TokenSchema
from src.database.connection import get_db
from src.dependencies.users import authenticate_user

user_router = APIRouter(prefix="/users")


@user_router.post(
    "/register/",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutputSchema,
)
async def register_user(
    user_register_schema: RegisterSchema,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
):
    user = await user_service.register_user(user_register_schema, session=session)
    user_schema = User.from_orm(user)
    email = user_schema.email
    background_tasks.add_task(user_service.send_activation_email, email)
    return user_schema


@user_router.post(
    "/login/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
)
async def login_user(
    user_login_schema: LoginSchema,
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
):
    user = await user_service.authenticate(**user_login_schema.dict(), session=session)
    user_schema = User.from_orm(user)
    access_token = auth_jwt.create_access_token(subject=user_schema.json())

    return TokenSchema(access_token=access_token)


@user_router.get(
    "/",
    tags=["users"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutputSchema],
)
async def get_users(session: AsyncSession = Depends(get_db)) -> list[UserOutputSchema]:
    result = await session.exec(select(User))
    return [UserOutputSchema.from_orm(user) for user in result.all()]


@user_router.get(
    "/profile/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_logged_user(
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    return UserOutputSchema.from_orm(request_user)


@user_router.get(
    "/{user_id}/",
    tags=["users"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_user(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> UserOutputSchema:
    result = await session.exec(select(User).where(User.id == user_id))
    return User.from_orm(result.first())


@user_router.get(
    "/profile/friends/",
    tags=["users-friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_user(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> list[FriendOutputSchema]:
    ...


@user_router.get(
    "/profile/friends/{friend_id}/",
    tags=["users-friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_friend_by_id(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> FriendOutputSchema:
    ...


@user_router.delete(
    "/profile/friends/{friend_id}/",
    tags=["users-friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend(user_id: UUID, session: AsyncSession = Depends(get_db)):
    ...


@user_router.post(
    "/{user_id}/add_friend/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def send_friend_request(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> FriendRequestOutputSchema:
    ...


@user_router.delete(
    "/{user_id}/remove_friend/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend(user_id: UUID, session: AsyncSession = Depends(get_db)):
    ...


@user_router.get(
    "/profile/friends/requests/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_friend_requests(
    session: AsyncSession = Depends(get_db),
) -> list[FriendRequestOutputSchema]:
    ...


@user_router.get(
    "/profile/friends/requests/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_friend_request_by_id(
    session: AsyncSession = Depends(get_db),
) -> FriendRequestOutputSchema:
    ...


@user_router.put(
    "/profile/friends/requests/{friend_request_id}/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def update_friend_request(
    friend_request_id: UUID, session: AsyncSession = Depends(get_db)
) -> FriendRequestOutputSchema:
    ...
