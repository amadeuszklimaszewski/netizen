from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.groups.models import GroupInputSchema
from src.apps.users.models import User


class GroupService:
    ...


class GroupRequestService:
    @classmethod
    async def create_group(schema: GroupInputSchema, user: User, session: AsyncSession):
        ...


class GroupMembershipService:
    ...
