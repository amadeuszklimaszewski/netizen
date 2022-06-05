from typing import Union
from uuid import UUID
from sqlmodel import select, update, and_, or_, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import PermissionDeniedException
from src.apps.groups.enums import GroupMemberStatus
from src.apps.groups.models import Group, GroupInputSchema, GroupMembership
from src.apps.users.models import User
from src.core.utils import get_object_by_id


class GroupService:
    @classmethod
    async def create_membership(
        cls,
        group: Group,
        user: User,
        membership_status: GroupMemberStatus,
        session: AsyncSession,
    ) -> GroupMembership:
        membership = GroupMembership(
            group_id=group.id,
            user_id=user.id,
            membership_status=membership_status,
        )
        session.add(membership)
        await session.commit()
        await session.refresh(membership)
        return membership

    @classmethod
    async def create_group(
        cls, schema: GroupInputSchema, user: User, session: AsyncSession
    ) -> Group:
        group_data = schema.dict()
        group = Group(**group_data)
        session.add(group)
        await session.commit()

        admin = await cls.create_membership(
            group=group,
            user=user,
            membership_status=GroupMemberStatus.ADMIN,
            session=session,
        )

        await session.refresh(group)
        return group

    @classmethod
    async def _find_membership(
        cls, group_id: UUID, user_id: UUID, session: AsyncSession
    ):
        membership: Union[GroupMembership, None] = (
            await session.exec(
                select(GroupMembership).where(
                    and_(
                        GroupMembership.group_id == group_id,
                        GroupMembership.user_id == user_id,
                    )
                )
            )
        ).first()
        return membership

    @classmethod
    async def _check_user_permissions(
        cls, group_id: UUID, user: User, session: AsyncSession
    ):
        membership = await cls._find_membership(
            group_id=group_id, user_id=user.id, session=session
        )
        if not membership or membership.membership_status != "ADMIN":
            raise PermissionDeniedException

    @classmethod
    async def update_group(
        cls, schema: GroupInputSchema, group_id: UUID, user: User, session: AsyncSession
    ) -> Group:
        await get_object_by_id(Table=Group, id=group_id, session=session)
        await cls._check_user_permissions(group_id=group_id, user=user, session=session)

        update_data = schema.dict()
        await session.exec(
            update(Group).where(Group.id == group_id).values(**update_data)
        )
        return (await session.exec(select(Group).where(Group.id == group_id))).first()

    @classmethod
    async def delete_group(cls, group_id: UUID, user: User, session: AsyncSession):
        await get_object_by_id(Table=Group, id=group_id, session=session)
        await cls._check_user_permissions(group_id=group_id, user=user, session=session)
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
                await session.exec(select(Group).where(Group.status != "CLOSED"))
            ).all()
        return (
            await session.exec(
                select(Group)
                .join(Group.members)
                .join(GroupMembership.user)
                .where(or_(User.id == request_user.id, Group.status != "CLOSED"))
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
        if not request_user and group.status == "CLOSED":
            raise PermissionDeniedException
        if request_user and group.status == "CLOSED":
            membership = await cls._find_membership(
                group_id=group.id, user_id=request_user.id, session=session
            )
            if membership is None:
                raise PermissionDeniedException
        return group
