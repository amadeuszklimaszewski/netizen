from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
        return Group.from_orm(group)

    @classmethod
    async def update_group(
        cls, schema: GroupInputSchema, user: User, session: AsyncSession
    ):
        ...
