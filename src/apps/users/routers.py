from uuid import UUID
from fastapi import BackgroundTasks, Depends, status
from fastapi.routing import APIRouter
from fastapi_another_jwt_auth import AuthJWT

from sqlmodel.ext.asyncio.session import AsyncSession

from src.settings import settings
from src.database.connection import get_db
from src.dependencies.users import authenticate_user
from src.apps.users.models import User
from src.apps.users.schemas import (
    LoginSchema,
    RegisterSchema,
    UserOutputSchema,
    FriendOutputSchema,
    FriendRequestOutputSchema,
    FriendRequestUpdateSchema,
)
from src.apps.users.services import FriendService, UserService
from src.apps.jwt.schemas import TokenOutputSchema
from src.apps.emails.schemas import EmailToken
from src.apps.emails.services import EmailService

from src.apps.posts.routers import user_post_router


user_router = APIRouter(prefix="/users")
user_router.include_router(user_post_router)


@user_router.post(
    "/register/",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutputSchema,
)
async def register_user(
    user_register_schema: RegisterSchema,
    background_tasks: BackgroundTasks,
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(),
    email_service: EmailService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> UserOutputSchema:
    user = await user_service.register_user(user_register_schema, session=session)

    user_email = user.email
    token = auth_jwt.create_access_token(subject=EmailToken(email=user_email).json())
    background_tasks.add_task(
        email_service.send_activation_email,
        user_email,
        token,
        settings.get_email_backend,
    )

    return UserOutputSchema.from_orm(user)


@user_router.post(
    "/login/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=TokenOutputSchema,
)
async def login_user(
    user_login_schema: LoginSchema,
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> TokenOutputSchema:
    user = await user_service.authenticate(**user_login_schema.dict(), session=session)
    user_schema = UserOutputSchema.from_orm(user)
    access_token = auth_jwt.create_access_token(subject=user_schema.json())

    return TokenOutputSchema(access_token=access_token)


@user_router.get(
    "/",
    tags=["users"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutputSchema],
)
async def get_users(
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[UserOutputSchema]:
    return [
        UserOutputSchema.from_orm(user)
        for user in (await user_service.get_user_list(session=session))
    ]


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
    user_id: UUID,
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> UserOutputSchema:
    user = await user_service.get_user_by_id(user_id=user_id, session=session)
    return UserOutputSchema.from_orm(user)


@user_router.get(
    "/profile/friends/",
    tags=["user-friends"],
    status_code=status.HTTP_200_OK,
    response_model=list[FriendOutputSchema],
)
async def get_user(
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[FriendOutputSchema]:
    return [
        FriendOutputSchema.from_orm(friend)
        for friend in (
            await friend_service.filter_friend_list(
                request_user=request_user, session=session
            )
        )
    ]


@user_router.get(
    "/profile/friends/{friend_id}/",
    tags=["user-friends"],
    status_code=status.HTTP_200_OK,
    response_model=FriendOutputSchema,
)
async def get_friend_by_id(
    friend_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> FriendOutputSchema:
    friend = await friend_service.filter_friend_by_id(
        friend_id=friend_id, request_user=request_user, session=session
    )
    return FriendOutputSchema.from_orm(friend)


@user_router.delete(
    "/profile/friends/{friend_id}/",
    tags=["user-friends"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend(
    friend_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await friend_service.delete_friend(
        friend_id=friend_id, request_user=request_user, session=session
    )
    return


@user_router.post(
    "/{user_id}/add-friend/",
    tags=["friends"],
    status_code=status.HTTP_201_CREATED,
    response_model=FriendRequestOutputSchema,
)
async def send_friend_request(
    user_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> FriendRequestOutputSchema:
    request = await friend_service.create_friend_request(
        user_id=user_id, request_user=request_user, session=session
    )
    return FriendRequestOutputSchema.from_orm(request)


@user_router.delete(
    "/{user_id}/remove-friend/",
    tags=["friends"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend(
    user_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await friend_service.delete_friend(
        friend_id=user_id, request_user=request_user, session=session
    )
    return


@user_router.get(
    "/profile/requests/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=list[FriendRequestOutputSchema],
)
async def get_received_friend_requests(
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[FriendRequestOutputSchema]:
    return [
        FriendRequestOutputSchema.from_orm(friend)
        for friend in (
            await friend_service.filter_received_friend_requests(
                request_user=request_user, session=session
            )
        )
    ]


@user_router.get(
    "/profile/requests/sent/",
    tags=["friends"],
    status_code=status.HTTP_200_OK,
    response_model=list[FriendRequestOutputSchema],
)
async def get_sent_friend_requests(
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[FriendRequestOutputSchema]:
    return [
        FriendRequestOutputSchema.from_orm(friend)
        for friend in (
            await friend_service.filter_sent_friend_requests(
                request_user=request_user, session=session
            )
        )
    ]


@user_router.get(
    "/profile/requests/sent/{friend_request_id}/",
    tags=["friends"],
    status_code=status.HTTP_200_OK,
    response_model=FriendRequestOutputSchema,
)
async def get_sent_friend_request_by_id(
    friend_request_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> FriendRequestOutputSchema:
    request = await friend_service.filter_sent_friend_request_by_id(
        friend_request_id=friend_request_id, request_user=request_user, session=session
    )
    return FriendRequestOutputSchema.from_orm(request)


@user_router.delete(
    "/profile/requests/sent/{friend_request_id}/",
    tags=["friends"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_friend_request(
    friend_request_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await friend_service.delete_friend_request(
        friend_request_id=friend_request_id, request_user=request_user, session=session
    )
    return


@user_router.get(
    "/profile/requests/{friend_request_id}/",
    tags=["friends"],
    status_code=status.HTTP_200_OK,
    response_model=FriendRequestOutputSchema,
)
async def get_received_friend_request_by_id(
    friend_request_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> FriendRequestOutputSchema:
    request = await friend_service.filter_received_friend_request_by_id(
        friend_request_id=friend_request_id, request_user=request_user, session=session
    )
    return FriendRequestOutputSchema.from_orm(request)


@user_router.put(
    "/profile/requests/{friend_request_id}/",
    tags=["friends"],
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
    response_model=FriendRequestOutputSchema,
)
async def update_friend_request(
    update_schema: FriendRequestUpdateSchema,
    friend_request_id: UUID,
    request_user: User = Depends(authenticate_user),
    friend_service: FriendService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> FriendRequestOutputSchema:
    request = await friend_service.update_friend_request(
        schema=update_schema,
        request_user=request_user,
        friend_request_id=friend_request_id,
        session=session,
    )
    return FriendRequestOutputSchema.from_orm(request)
