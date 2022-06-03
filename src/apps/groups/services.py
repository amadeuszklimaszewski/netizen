from uuid import UUID
from sqlmodel import select, update, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import PermissionDenied
from src.apps.groups.enums import GroupMemberStatus
from src.apps.groups.models import Group, GroupInputSchema, GroupMembership
from src.apps.users.models import User


class GroupService:
    @classmethod
    async def create_membership(
        cls,
        group: Group,
        user: User,
        membership_status: GroupMemberStatus,
        session: AsyncSession,
    ):
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
    ):
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
    async def update_group(
        cls, schema: GroupInputSchema, group_id: UUID, user: User, session: AsyncSession
    ):
        membership: GroupMembership = (
            await session.exec(
                select(GroupMembership).where(
                    and_(
                        GroupMembership.group_id == group_id,
                        GroupMembership.user_id == user.id,
                    )
                )
            )
        ).first()
        if not membership or membership.membership_status != "ADMIN":
            raise PermissionDenied

        update_data = schema.dict()
        await session.exec(
            update(Group).where(Group.id == group_id).values(**update_data)
        )
        return (await session.exec(select(Group).where(Group.id == group_id))).first()
