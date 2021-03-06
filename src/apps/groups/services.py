from typing import Union
from uuid import UUID
from sqlmodel import select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import (
    AlreadyExistsException,
    PermissionDeniedException,
    DoesNotExistException,
    GroupRequestAlreadyHandled,
)
from src.apps.groups.enums import GroupMemberStatus, GroupRequestStatus, GroupStatus
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
from src.apps.groups.permissions import (
    validate_user_is_admin,
    validate_user_is_moderator_or_admin,
)
from src.apps.users.models import User
from src.core.utils import get_object_by_id


class GroupService:

    # --- --- Group members --- ---

    @classmethod
    async def create_membership(
        cls,
        group_id: UUID,
        user: User,
        membership_status: GroupMemberStatus,
        session: AsyncSession,
    ) -> GroupMembership:
        membership = GroupMembership(
            group_id=group_id,
            user_id=user.id,
            membership_status=membership_status,
        )
        session.add(membership)
        await session.commit()
        await session.refresh(membership)
        return membership

    @classmethod
    async def update_membership(
        cls,
        schema: GroupMembershipUpdateSchema,
        group_id: UUID,
        membership_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupMembership:
        request_user_membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=request_user.id, session=session
        )
        await validate_user_is_moderator_or_admin(membership=request_user_membership)
        membership = await get_object_by_id(
            Table=GroupMembership, id=membership_id, session=session
        )
        update_data = schema.dict()
        await session.exec(
            update(GroupMembership)
            .where(GroupMembership.id == membership_id)
            .values(**update_data)
        )

        await session.refresh(membership)

        return membership

    @classmethod
    async def delete_membership_by_id(
        cls,
        group_id: UUID,
        membership_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        request_user_membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=request_user.id, session=session
        )
        await validate_user_is_moderator_or_admin(membership=request_user_membership)
        membership = await get_object_by_id(
            Table=GroupMembership, id=membership_id, session=session
        )
        await session.delete(membership)
        await session.commit()
        return

    @classmethod
    async def delete_membership_by_user_id(
        cls,
        group_id: UUID,
        user: User,
        session: AsyncSession,
    ):
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=user.id, session=session
        )

        await session.delete(membership)
        await session.commit()
        return

    @classmethod
    async def _find_membership(
        cls,
        group_id: UUID,
        user_id: UUID,
        session: AsyncSession,
    ) -> Union[GroupMembership, None]:
        group: Group = await get_object_by_id(Table=Group, id=group_id, session=session)
        membership: Union[GroupMembership, None] = (
            await session.exec(
                select(GroupMembership).where(
                    (GroupMembership.group_id == group_id)
                    & (GroupMembership.user_id == user_id)
                )
            )
        ).first()
        return membership

    @classmethod
    async def _find_membership_or_raise_exception(
        cls,
        group_id: UUID,
        user_id: UUID,
        session: AsyncSession,
    ) -> GroupMembership:
        membership = await cls._find_membership(
            group_id=group_id, user_id=user_id, session=session
        )
        if membership is None:
            raise PermissionDeniedException("User is not a member of this group")
        return membership

    @classmethod
    async def filter_get_group_members_list(
        cls,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> list[GroupMembership | None]:
        group = await cls.filter_get_group_by_id(
            group_id=group_id, request_user=request_user, session=session
        )
        return (
            await session.exec(
                select(GroupMembership).where(GroupMembership.group_id == group.id)
            )
        ).all()

    @classmethod
    async def filter_get_group_member_by_id(
        cls,
        group_id: UUID,
        membership_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        group = await cls.filter_get_group_by_id(
            group_id=group_id, request_user=request_user, session=session
        )

        membership = await get_object_by_id(
            Table=GroupMembership, id=membership_id, session=session
        )
        return membership

    # --- --- Groups --- ---

    @classmethod
    async def create_group(
        cls,
        schema: GroupInputSchema,
        user: User,
        session: AsyncSession,
    ) -> Group:
        group_data = schema.dict()
        group = Group(**group_data)
        session.add(group)
        await session.commit()

        admin = await cls.create_membership(
            group_id=group.id,
            user=user,
            membership_status=GroupMemberStatus.ADMIN,
            session=session,
        )

        await session.refresh(group)
        return group

    @classmethod
    async def update_group(
        cls,
        schema: GroupInputSchema,
        group_id: UUID,
        user: User,
        session: AsyncSession,
    ) -> Group:
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=user.id, session=session
        )
        await validate_user_is_admin(membership=membership)

        update_data = schema.dict()
        await session.exec(
            update(Group).where(Group.id == group_id).values(**update_data)
        )
        group = await get_object_by_id(Table=Group, id=group_id, session=session)
        return group

    @classmethod
    async def delete_group(
        cls,
        group_id: UUID,
        user: User,
        session: AsyncSession,
    ):
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=user.id, session=session
        )
        await validate_user_is_admin(membership=membership)

        group = (await session.exec(select(Group).where(Group.id == group_id))).first()
        await session.delete(group)
        await session.commit()
        return

    @classmethod
    async def filter_get_group_list(
        cls,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> list[Group]:
        if not request_user:
            return (
                await session.exec(
                    select(Group).where(Group.status != GroupStatus.CLOSED)
                )
            ).all()
        return (
            await session.exec(
                select(Group)
                .join(Group.members)
                .join(GroupMembership.user)
                .where(
                    (User.id == request_user.id) | (Group.status != GroupStatus.CLOSED)
                )
            )
        ).all()

    @classmethod
    async def filter_get_group_by_id(
        cls,
        group_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> Group:
        group: Group = await get_object_by_id(Table=Group, id=group_id, session=session)
        if not request_user and group.status == GroupStatus.CLOSED:
            raise PermissionDeniedException
        if request_user and group.status == GroupStatus.CLOSED:
            membership = await cls._find_membership_or_raise_exception(
                group_id=group_id, user_id=request_user.id, session=session
            )
        return group

    # --- ---- Group requests --- ---

    @classmethod
    async def create_group_request(
        cls,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupRequest:
        group: Group = await get_object_by_id(Table=Group, id=group_id, session=session)

        if await cls._find_membership(
            group_id=group.id, user_id=request_user.id, session=session
        ):
            raise AlreadyExistsException("User is already a member of this group")

        request = GroupRequest(
            group=group, user=request_user, status=GroupRequestStatus.PENDING
        )
        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request

    @classmethod
    async def update_group_request(
        cls,
        schema: GroupRequestUpdateSchema,
        group_id: UUID,
        request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=request_user.id, session=session
        )
        await validate_user_is_moderator_or_admin(membership=membership)
        request = await cls._find_group_request(
            group_id=group_id, request_id=request_id, session=session
        )

        if (
            request.status == GroupRequestStatus.ACCEPTED
            or request.status == GroupRequestStatus.DENIED
        ):
            raise GroupRequestAlreadyHandled("Group request already denied or accepted")
        update_data = schema.dict()
        if update_data["status"] == GroupRequestStatus.ACCEPTED:
            await cls.create_membership(
                group_id=group_id,
                user=request.user,
                membership_status=GroupMemberStatus.REGULAR,
                session=session,
            )
        await session.exec(
            update(GroupRequest)
            .where(GroupRequest.id == request_id)
            .values(**update_data)
        )

        return (
            await session.exec(
                select(GroupRequest).where(GroupRequest.id == request_id)
            )
        ).first()

    @classmethod
    async def _find_group_request(
        cls,
        group_id: UUID,
        request_id: UUID,
        session: AsyncSession,
    ) -> GroupRequest:
        group: Group = await get_object_by_id(Table=Group, id=group_id, session=session)
        request: Union[GroupRequest, None] = (
            await session.exec(
                select(GroupRequest).where(
                    (GroupRequest.id == request_id)
                    & (GroupRequest.group_id == group_id)
                )
            )
        ).first()
        if request is None:
            raise DoesNotExistException("Group request with given ID does not exist")
        return request

    @classmethod
    async def filter_get_group_request_list(
        cls,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> list[GroupRequest]:
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=request_user.id, session=session
        )
        await validate_user_is_moderator_or_admin(membership=membership)
        return (
            await session.exec(
                select(GroupRequest).where(
                    (GroupRequest.group_id == group_id)
                    & (GroupRequest.status == GroupRequestStatus.PENDING)
                )
            )
        ).all()

    @classmethod
    async def filter_get_group_request_by_id(
        cls,
        group_id: UUID,
        request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupRequest:
        membership = await cls._find_membership_or_raise_exception(
            group_id=group_id, user_id=request_user.id, session=session
        )
        await validate_user_is_moderator_or_admin(membership=membership)
        request = await cls._find_group_request(
            group_id=group_id, request_id=request_id, session=session
        )
        return request

    @classmethod
    async def filter_get_user_group_request_list(
        cls,
        request_user: User,
        session: AsyncSession,
    ) -> list[GroupRequest]:
        requests = (
            await session.exec(
                select(GroupRequest).where(
                    (GroupRequest.user_id == request_user.id)
                    & (GroupRequest.status == GroupRequestStatus.PENDING)
                )
            )
        ).all()
        return requests

    @classmethod
    async def filter_get_user_group_request_by_id(
        cls,
        request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupRequest:
        request = await get_object_by_id(
            Table=GroupRequest, id=request_id, session=session
        )
        if request.user != request_user:
            raise PermissionDeniedException("Invalid group request id.")
        return request

    @classmethod
    async def delete_user_group_request(
        cls,
        request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        request = await cls.filter_get_user_group_request_by_id(
            request_id=request_id, request_user=request_user, session=session
        )
        if request.status != GroupRequestStatus.PENDING:
            raise GroupRequestAlreadyHandled("Group request was already handled.")
        await session.delete(request)
        await session.commit()
        return
