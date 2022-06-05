from unicodedata import name
import pytest
from sqlalchemy.orm import selectinload
from sqlmodel import select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.groups.models import (
    Group,
    GroupInputSchema,
    GroupMembership,
    GroupOutputSchema,
)
from src.apps.groups.services import GroupService
from src.apps.users.models import User
from src.core.exceptions import PermissionDeniedException


@pytest.mark.asyncio
async def test_check_user_permissions(
    public_group_in_db: Group,
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
):
    try:
        await GroupService._check_user_permissions(
            group_id=public_group_in_db.id, user=user_in_db, session=session
        )
    except PermissionDeniedException as exc:
        assert False, f"Exception raised: {exc}"

    with pytest.raises(PermissionDeniedException):
        await GroupService._check_user_permissions(
            group_id=public_group_in_db.id, user=other_user_in_db, session=session
        )

    await session.exec(
        update(GroupMembership)
        .where(GroupMembership.user_id == user_in_db.id)
        .values({"membership_status": "REGULAR"})
    )
    await session.refresh(user_in_db)
    with pytest.raises(PermissionDeniedException):
        await GroupService._check_user_permissions(
            group_id=public_group_in_db.id, user=other_user_in_db, session=session
        )


@pytest.mark.asyncio
async def test_group_service_correctly_creates_group(
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
async def test_group_service_correctly_deletes_group(
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    await GroupService.delete_group(
        group_id=public_group_in_db.id, user=user_in_db, session=session
    )
    memberships = (
        await session.exec(
            select(GroupMembership).where(
                GroupMembership.group_id == public_group_in_db.id
            )
        )
    ).all()
    assert len(memberships) == 0
    group = (
        await session.exec(select(Group).where(Group.id == public_group_in_db.id))
    ).first()
    assert group == None


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


@pytest.mark.asyncio
async def test_group_service_correctly_filters_group_by_id(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    group = await GroupService.filter_get_group_by_id(
        group_id=public_group_in_db.id, request_user=user_in_db, session=session
    )
    assert group.name == public_group_in_db.name
    assert group.description == public_group_in_db.description
    assert group.status == public_group_in_db.status

    closed_group = await GroupService.filter_get_group_by_id(
        group_id=closed_group_in_db.id, request_user=user_in_db, session=session
    )
    assert closed_group.name == closed_group_in_db.name
    assert closed_group.description == closed_group_in_db.description
    assert closed_group.status == closed_group_in_db.status


@pytest.mark.asyncio
async def test_group_service_correctly_filters_public_group_by_id_with_no_user(
    public_group_in_db: Group,
    private_group_in_db: Group,
    session: AsyncSession,
):
    group = await GroupService.filter_get_group_by_id(
        group_id=public_group_in_db.id, request_user=None, session=session
    )
    assert group.name == public_group_in_db.name
    assert group.description == public_group_in_db.description
    assert group.status == public_group_in_db.status

    private_group = await GroupService.filter_get_group_by_id(
        group_id=private_group_in_db.id, request_user=None, session=session
    )
    assert private_group.name == private_group_in_db.name
    assert private_group.description == private_group_in_db.description
    assert private_group.status == private_group_in_db.status


@pytest.mark.asyncio
async def test_group_service_raises_permission_denied_exception_with_closed_group(
    other_user_in_db: User,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        group = await GroupService.filter_get_group_by_id(
            group_id=closed_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        group = await GroupService.filter_get_group_by_id(
            group_id=closed_group_in_db.id, request_user=None, session=session
        )
