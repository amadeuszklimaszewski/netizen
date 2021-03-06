from uuid import uuid4
import pytest
from sqlalchemy.orm import selectinload
from sqlmodel import select, update, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.groups.models import (
    Group,
    GroupMembership,
    GroupRequest,
)
from src.apps.groups.schemas import (
    GroupInputSchema,
    GroupMembershipUpdateSchema,
    GroupRequestUpdateSchema,
)
from src.apps.groups.services import GroupService
from src.apps.users.models import User
from src.core.exceptions import (
    DoesNotExistException,
    GroupRequestAlreadyHandled,
    PermissionDeniedException,
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
        group_id=closed_group_in_db.id,
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
async def test_filter_public_group_by_id_raises_permission_denied_exception_with_closed_group(
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


@pytest.mark.asyncio
async def test_group_service_correctly_creates_group_request(
    other_user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    request = await GroupService.create_group_request(
        group_id=public_group_in_db.id, request_user=other_user_in_db, session=session
    )
    assert request.user == other_user_in_db
    assert request.group == public_group_in_db
    assert request.status == "PENDING"


@pytest.mark.asyncio
async def test_group_service_correctly_removes_user_from_group(
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    await GroupService.delete_membership_by_user_id(
        group_id=public_group_in_db.id, user=user_in_db, session=session
    )
    membership = (
        await session.exec(
            select(GroupMembership).where(
                and_(
                    GroupMembership.user_id == user_in_db.id,
                    GroupMembership.group_id == public_group_in_db.id,
                )
            )
        )
    ).first()
    assert membership == None


@pytest.mark.asyncio
async def test_remove_membership_by_user_id_raises_exception_when_user_is_not_a_member(
    other_user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        await GroupService.delete_membership_by_user_id(
            group_id=public_group_in_db.id, user=other_user_in_db, session=session
        )


@pytest.mark.asyncio
async def test_group_service_correctly_filters_group_requests(
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    result = await GroupService.filter_get_group_request_list(
        group_id=public_group_in_db.id, request_user=user_in_db, session=session
    )
    assert len(result) == 1
    assert result[0].id == group_request_in_db.id
    assert result[0].user_id == group_request_in_db.user_id
    assert result[0].group_id == group_request_in_db.group_id


@pytest.mark.asyncio
async def test_filter_get_group_request_list_correctly_excludes_accepted_requests(
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    group_request_in_db.status = "ACCEPTED"
    session.add(group_request_in_db)
    await session.commit()

    result = await GroupService.filter_get_group_request_list(
        group_id=public_group_in_db.id, request_user=user_in_db, session=session
    )
    assert len(result) == 0


@pytest.mark.asyncio
async def test_filter_get_group_request_list_raises_permission_denied_with_invalid_user(
    other_user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        result = await GroupService.filter_get_group_request_list(
            group_id=public_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_filters_group_request_by_id(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    request: GroupRequest = await GroupService.filter_get_group_request_by_id(
        group_id=public_group_in_db.id,
        request_id=group_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert request.group_id == group_request_in_db.group_id
    assert request.user_id == group_request_in_db.user_id
    assert request.status == group_request_in_db.status


@pytest.mark.asyncio
async def test_group_service_raises_does_not_exist_exception_on_get_invalid_request_id(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        request: GroupRequest = await GroupService.filter_get_group_request_by_id(
            group_id=public_group_in_db.id,
            request_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_updates_group_request(
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    schema = GroupRequestUpdateSchema(**{"status": "ACCEPTED"})
    request = await GroupService.update_group_request(
        schema=schema,
        group_id=public_group_in_db.id,
        request_id=group_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert request.status == schema.status
    assert request.group_id == group_request_in_db.group_id
    assert request.user_id == group_request_in_db.user_id


@pytest.mark.asyncio
async def test_group_service_correctly_creates_membership_on_accepting_group_request(
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    schema = GroupRequestUpdateSchema(**{"status": "ACCEPTED"})
    request = await GroupService.update_group_request(
        schema=schema,
        group_id=public_group_in_db.id,
        request_id=group_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    membership = (
        await session.exec(
            select(GroupMembership).where(
                GroupMembership.user_id == group_request_in_db.user_id
            )
        )
    ).first()
    assert membership != None
    assert membership.group_id == group_request_in_db.group_id
    assert membership.membership_status == "REGULAR"


@pytest.mark.asyncio
async def test_group_service_raises_group_request_already_handled_on_duplicated_update_request(
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    schema = GroupRequestUpdateSchema(**{"status": "ACCEPTED"})
    request = await GroupService.update_group_request(
        schema=schema,
        group_id=public_group_in_db.id,
        request_id=group_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    with pytest.raises(GroupRequestAlreadyHandled):
        request = await GroupService.update_group_request(
            schema=schema,
            group_id=public_group_in_db.id,
            request_id=group_request_in_db.id,
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_filters_get_group_members_list(
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    members = await GroupService.filter_get_group_members_list(
        group_id=public_group_in_db.id, request_user=user_in_db, session=session
    )
    assert len(members) == 1
    assert members[0].user_id == user_in_db.id


@pytest.mark.asyncio
async def test_group_service_correctly_filters_get_group_members_list_with_other_user(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    session: AsyncSession,
):
    public_members = await GroupService.filter_get_group_members_list(
        group_id=public_group_in_db.id, request_user=other_user_in_db, session=session
    )
    assert len(public_members) == 1
    assert public_members[0].user_id == user_in_db.id

    private_members = await GroupService.filter_get_group_members_list(
        group_id=private_group_in_db.id, request_user=other_user_in_db, session=session
    )
    assert len(private_members) == 1
    assert private_members[0].user_id == user_in_db.id


@pytest.mark.asyncio
async def test_group_service_correctly_filters_get_closed_group_members_list(
    user_in_db: User,
    other_user_in_db: User,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    members = await GroupService.filter_get_group_members_list(
        group_id=closed_group_in_db.id, request_user=user_in_db, session=session
    )
    assert len(members) == 1
    assert members[0].user_id == user_in_db.id


@pytest.mark.asyncio
async def test_group_service_filters_get_closed_group_members_raises_permission_denied_exception(
    other_user_in_db: User,
    closed_group_in_db: Group,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        members = await GroupService.filter_get_group_members_list(
            group_id=closed_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_filters_group_membership_by_id(
    user_in_db: User,
    public_group_in_db: Group,
    group_membership_in_db: GroupMembership,
    session: AsyncSession,
):

    membership = await GroupService.filter_get_group_member_by_id(
        group_id=public_group_in_db.id,
        membership_id=group_membership_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert membership.group_id == group_membership_in_db.group_id
    assert membership.user_id == group_membership_in_db.user_id
    assert membership.membership_status == group_membership_in_db.membership_status


@pytest.mark.asyncio
async def test_group_service_correctly_updates_group_membership(
    user_in_db: User,
    public_group_in_db: Group,
    group_membership_in_db: GroupMembership,
    session: AsyncSession,
):
    schema = GroupMembershipUpdateSchema(**{"membership_status": "MODERATOR"})
    membership = await GroupService.update_membership(
        schema=schema,
        group_id=public_group_in_db.id,
        membership_id=group_membership_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert membership.membership_status == "MODERATOR"


@pytest.mark.asyncio
async def test_update_group_membership_correctly_raises_exceptions(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    group_membership_in_db: GroupMembership,
    session: AsyncSession,
):
    schema = GroupMembershipUpdateSchema(**{"membership_status": "MODERATOR"})
    with pytest.raises(PermissionDeniedException):
        membership = await GroupService.update_membership(
            schema=schema,
            group_id=public_group_in_db.id,
            membership_id=group_membership_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        membership = await GroupService.update_membership(
            schema=schema,
            group_id=uuid4(),
            membership_id=group_membership_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        membership = await GroupService.update_membership(
            schema=schema,
            group_id=public_group_in_db.id,
            membership_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_deletes_group_membership_by_id(
    user_in_db: User,
    public_group_in_db: Group,
    group_membership_in_db: GroupMembership,
    session: AsyncSession,
):
    await GroupService.delete_membership_by_id(
        group_id=public_group_in_db.id,
        membership_id=group_membership_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    result = (
        await session.exec(
            select(GroupMembership).where(
                GroupMembership.id == group_membership_in_db.id
            )
        )
    ).first()
    assert result == None


@pytest.mark.asyncio
async def test_group_service_delete_group_membership_by_id_correctly_raises_exceptions(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    group_membership_in_db: GroupMembership,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        await GroupService.delete_membership_by_id(
            group_id=public_group_in_db.id,
            membership_id=group_membership_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        await GroupService.delete_membership_by_id(
            group_id=public_group_in_db.id,
            membership_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_filters_get_user_group_request_list(
    other_user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    requests = await GroupService.filter_get_user_group_request_list(
        request_user=other_user_in_db, session=session
    )
    assert len(requests) == 1
    assert requests[0].id == group_request_in_db.id


@pytest.mark.asyncio
async def test_group_service_correctly_filters_get_user_group_request_by_id(
    other_user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    request = await GroupService.filter_get_user_group_request_by_id(
        request_id=group_request_in_db.id,
        request_user=other_user_in_db,
        session=session,
    )
    assert request.user_id == group_request_in_db.user_id
    assert request.group_id == group_request_in_db.group_id


@pytest.mark.asyncio
async def test_filter_get_user_group_request_by_id_raises_exception_with_invalid_id(
    other_user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        request = await GroupService.filter_get_user_group_request_by_id(
            request_id=uuid4(),
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_filter_get_user_group_request_by_id_raises_exception_with_wrong_user(
    user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        request = await GroupService.filter_get_user_group_request_by_id(
            request_id=group_request_in_db.id,
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_service_correctly_deletes_user_group_request(
    other_user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    await GroupService.delete_user_group_request(
        request_id=group_request_in_db.id,
        request_user=other_user_in_db,
        session=session,
    )
    result = (await session.exec(select(GroupRequest))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_user_group_request_raises_exception_with_handled_request(
    other_user_in_db: User,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    await session.exec(
        update(GroupRequest)
        .where(GroupRequest.id == group_request_in_db.id)
        .values(**{"status": "DENIED"})
    )
    with pytest.raises(GroupRequestAlreadyHandled):
        await GroupService.delete_user_group_request(
            request_id=group_request_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    result = (await session.exec(select(GroupRequest))).all()
    assert len(result) == 1
