from fastapi import Response, status
from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.groups.models import (
    Group,
    GroupInputSchema,
    GroupMembership,
    GroupOutputSchema,
)
from src.apps.groups.services import GroupService
from src.apps.users.models import User, UserOutputSchema


@pytest.mark.asyncio
async def test_group_service_correctly_creates_group(
    client: AsyncClient,
    user_in_db: User,
    group_create_data: dict[str, str],
    session: AsyncSession,
):
    schema = GroupInputSchema(**group_create_data)
    group = await GroupService.create_group(
        user=user_in_db, schema=schema, session=session
    )
    assert group.name == group_create_data["name"]
    assert group.description == group_create_data["description"]
    assert group.status == group_create_data["status"]

    result = await session.exec(select(Group).options(selectinload(Group.members)))
    groups = result.all()
    assert len(groups) == 1
    group_in_db = groups[0]
    assert group_in_db == group
    assert len(group_in_db.members) == 1
    assert group_in_db.members[0].user == user_in_db


@pytest.mark.asyncio
async def test_group_service_correctly_updates_group(
    user_in_db: User,
    public_group_in_db: Group,
    group_update_data: dict[str, str],
    session: AsyncSession,
):
    schema = GroupInputSchema(**group_update_data)
    group = await GroupService.update_group(
        schema=schema, group_id=public_group_in_db.id, user=user_in_db, session=session
    )
    assert group.name == group_update_data["name"]
    assert group.description == group_update_data["description"]
    assert group.status == group_update_data["status"]

    result = await session.exec(select(Group).options(selectinload(Group.members)))
    groups = result.all()
    assert len(groups) == 1
    group_in_db = groups[0]
    assert group_in_db == group


@pytest.mark.asyncio
async def test_group_service_correctly_filters_groups_without_user(
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    groups = await GroupService.filter_get_group_list(
        request_user=None, session=session
    )
    assert len(groups) == 2
    assert public_group_in_db in groups
    assert private_group_in_db in groups
    assert closed_group_in_db not in groups


@pytest.mark.asyncio
async def test_group_service_correctly_filters_groups_without_user(
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    groups = await GroupService.filter_get_group_list(
        request_user=None, session=session
    )
    assert len(groups) == 2
    assert public_group_in_db in groups
    assert private_group_in_db in groups
    assert closed_group_in_db not in groups


@pytest.mark.asyncio
async def test_group_service_correctly_filters_groups_with_user_in_all_groups(
    user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    groups = await GroupService.filter_get_group_list(
        request_user=user_in_db, session=session
    )
    assert len(groups) == 3
    assert public_group_in_db in groups
    assert private_group_in_db in groups
    assert closed_group_in_db in groups


@pytest.mark.asyncio
async def test_group_service_correctly_filters_groups_with_user_not_in_any_group(
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    groups = await GroupService.filter_get_group_list(
        request_user=other_user_in_db, session=session
    )
    assert len(groups) == 2
    assert public_group_in_db in groups
    assert private_group_in_db in groups
    assert closed_group_in_db not in groups


@pytest.mark.asyncio
async def test_group_service_correctly_filters_groups_with_user_in_closed_group(
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    await GroupService.create_membership(
        group=closed_group_in_db,
        user=other_user_in_db,
        membership_status="REGULAR",
        session=session,
    )
    groups = await GroupService.filter_get_group_list(
        request_user=other_user_in_db, session=session
    )
    assert len(groups) == 3
    assert public_group_in_db in groups
    assert private_group_in_db in groups
    assert closed_group_in_db in groups
