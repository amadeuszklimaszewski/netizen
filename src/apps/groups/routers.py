from uuid import UUID
from typing import Union

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.connection import get_db
from src.apps.users.models import User
from src.dependencies.users import authenticate_user, get_user_or_none
from src.apps.groups.models import (
    GroupMembershipOutputSchema,
    GroupMembershipUpdateSchema,
    GroupOutputSchema,
    GroupInputSchema,
    GroupRequestOutputSchema,
    GroupRequestUpdateSchema,
)
from src.apps.groups.services import GroupService
from src.apps.posts.routers import group_post_router

group_router = APIRouter(prefix="/groups")
group_router.include_router(group_post_router)


@group_router.get(
    "/requests/",
    tags=["user-group-requests"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_user_group_requests(
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> list[GroupRequestOutputSchema]:
    return [
        GroupRequestOutputSchema.from_orm(group_request)
        for group_request in (
            await group_service.filter_get_user_group_request_list(
                request_user=request_user, session=session
            )
        )
    ]


@group_router.get(
    "/requests/{request_id}/",
    tags=["user-group-requests"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def get_user_group_request_by_id(
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupRequestOutputSchema:
    request = await group_service.filter_get_user_group_request_by_id(
        request_id=request_id,
        request_user=request_user,
        session=session,
    )
    return GroupRequestOutputSchema.from_orm(request)


@group_router.delete(
    "/requests/{request_id}/",
    tags=["user-group-requests"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_group_request(
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupRequestOutputSchema:
    await group_service.delete_user_group_request(
        request_id=request_id,
        request_user=request_user,
        session=session,
    )
    return {}


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
    return [
        GroupOutputSchema.from_orm(group)
        for group in (
            await group_service.filter_get_group_list(
                request_user=request_user, session=session
            )
        )
    ]


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
    group = await group_service.filter_get_group_by_id(
        group_id=group_id, request_user=request_user, session=session
    )
    return GroupOutputSchema.from_orm(group)


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
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    await group_service.delete_group(
        group_id=group_id, user=request_user, session=session
    )
    return {}


@group_router.delete(
    "/{group_id}/leave/",
    tags=["group-members"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leave_group(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    await group_service.delete_membership_by_user_id(
        group_id=group_id, user=request_user, session=session
    )
    return {}


@group_router.post(
    "/{group_id}/join/",
    tags=["user-group-requests"],
    status_code=status.HTTP_201_CREATED,
    response_model=GroupRequestOutputSchema,
)
async def join_group(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupRequestOutputSchema:
    request = await group_service.create_group_request(
        group_id=group_id, request_user=request_user, session=session
    )
    return GroupRequestOutputSchema.from_orm(request)


@group_router.get(
    "/{group_id}/requests/",
    tags=["group-requests"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_group_requests(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> list[GroupRequestOutputSchema]:
    return [
        GroupRequestOutputSchema.from_orm(group_request)
        for group_request in (
            await group_service.filter_get_group_request_list(
                group_id=group_id, request_user=request_user, session=session
            )
        )
    ]


@group_router.get(
    "/{group_id}/requests/{request_id}/",
    tags=["group-requests"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def get_group_request_by_id(
    group_id: UUID,
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupRequestOutputSchema:
    request = await group_service.filter_get_group_request_by_id(
        group_id=group_id,
        request_id=request_id,
        request_user=request_user,
        session=session,
    )
    return GroupRequestOutputSchema.from_orm(request)


@group_router.put(
    "/{group_id}/requests/{request_id}/",
    tags=["group-requests"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def update_group_request(
    update_schema: GroupRequestUpdateSchema,
    group_id: UUID,
    request_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupRequestOutputSchema:
    request = await group_service.update_group_request(
        schema=update_schema,
        group_id=group_id,
        request_id=request_id,
        request_user=request_user,
        session=session,
    )
    return GroupRequestOutputSchema.from_orm(request)


@group_router.get(
    "/{group_id}/members/",
    tags=["group-members"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMembershipOutputSchema],
)
async def get_group_members(
    group_id: UUID,
    group_service: GroupService = Depends(),
    request_user: Union[User, None] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_db),
) -> list[GroupMembershipOutputSchema]:
    return [
        GroupMembershipOutputSchema.from_orm(member)
        for member in await group_service.filter_get_group_members_list(
            group_id=group_id, request_user=request_user, session=session
        )
    ]


@group_router.get(
    "/{group_id}/members/{membership_id}/",
    tags=["group-members"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMembershipOutputSchema,
)
async def get_group_member_by_id(
    group_id: UUID,
    membership_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_db),
) -> GroupMembershipOutputSchema:
    membership = await group_service.filter_get_group_member_by_id(
        group_id=group_id,
        membership_id=membership_id,
        request_user=request_user,
        session=session,
    )
    return GroupMembershipOutputSchema.from_orm(membership)


@group_router.put(
    "/{group_id}/members/{membership_id}/",
    tags=["group-members"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMembershipOutputSchema,
)
async def update_group_member(
    schema: GroupMembershipUpdateSchema,
    group_id: UUID,
    membership_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> GroupMembershipOutputSchema:
    membership = await group_service.update_membership(
        schema=schema,
        group_id=group_id,
        membership_id=membership_id,
        request_user=request_user,
        session=session,
    )
    return GroupMembershipOutputSchema.from_orm(membership)


@group_router.delete(
    "/{group_id}/members/{membership_id}/",
    tags=["group-members"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_member(
    group_id: UUID,
    membership_id: UUID,
    group_service: GroupService = Depends(),
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    await group_service.delete_membership_by_id(
        group_id=group_id,
        membership_id=membership_id,
        request_user=request_user,
        session=session,
    )
    return {}
