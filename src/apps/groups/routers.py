from http.client import HTTPResponse
from uuid import UUID
from typing import Union
from fastapi import BackgroundTasks, Depends, status
from fastapi.routing import APIRouter
from fastapi_another_jwt_auth import AuthJWT

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.users.models import User
from src.database.connection import get_db
from src.dependencies.users import authenticate_user, get_user_or_none

from src.apps.groups.models import (
    GroupMembership,
    GroupMembershipOutputSchema,
    GroupOutputSchema,
    GroupInputSchema,
    Group,
    GroupRequestOutputSchema,
)
from src.apps.groups.services import GroupService


group_router = APIRouter(prefix="/groups")

# dependencies=[Depends(authenticate_user)]


@group_router.get(
    "/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupOutputSchema],
)
async def get_groups(
    group_service: GroupService = Depends(),
    request_user: Union[User, None] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_db),
) -> list[GroupOutputSchema]:
    return (await session.exec(select(Group))).all()


@group_router.get(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupOutputSchema,
)
async def get_group_by_id(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: Union[User, None] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_db),
) -> GroupOutputSchema:
    return (await session.exec(select(Group).where(Group.id == group_id))).first()


@group_router.post(
    "/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=GroupOutputSchema,
)
async def create_group(
    group_input_schema: GroupInputSchema,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupOutputSchema:
    group = await group_service.create_group(
        schema=group_input_schema, user=request_user, session=session
    )
    return GroupOutputSchema.from_orm(group)


@group_router.put(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupOutputSchema,
)
async def update_group(
    update_schema: GroupInputSchema,
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupOutputSchema:
    updated_group = await group_service.update_group(
        schema=update_schema, group_id=group_id, user=request_user, session=session
    )
    return GroupOutputSchema.from_orm(updated_group)


@group_router.delete(
    "/{group_id}/", tags=["groups"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_group(
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.get(
    "/{group_id}/requests/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_group_requests(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.get(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def get_group_request_by_id(
    group_id: UUID,
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.put(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def update_group_request(
    group_id: UUID,
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.post(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=GroupRequestOutputSchema,
)
async def join_to_group(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.delete(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leave_group(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.get(
    "/{group_id}/members/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMembershipOutputSchema],
)
async def get_group_members(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: Union[User, None] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.get(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMembershipOutputSchema,
)
async def get_group_member_by_id(
    group_id: UUID,
    member_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@group_router.post(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMembershipOutputSchema,
)
async def update_group_member(
    group_id: UUID,
    member_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...
