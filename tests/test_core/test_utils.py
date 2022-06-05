import pytest
from uuid import uuid4
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.utils import get_object_by_id
from src.core.exceptions import DoesNotExistException, InvalidTableException
from src.apps.groups.models import Group
from src.apps.users.models import User


class InvalidTable(SQLModel):
    ...


@pytest.mark.asyncio
async def test_get_object_by_id_correctly_returns_object(
    user_in_db: User,
    group_in_db: Group,
    session: AsyncSession,
):
    user = await get_object_by_id(Table=User, id=user_in_db.id, session=session)
    assert user == user_in_db

    group = await get_object_by_id(Table=Group, id=group_in_db.id, session=session)
    assert group == group_in_db


@pytest.mark.asyncio
async def test_get_object_by_id_correctly_raises_does_not_exist_exception(
    user_in_db: User,
    group_in_db: Group,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        user = await get_object_by_id(Table=User, id=uuid4(), session=session)
    with pytest.raises(DoesNotExistException):
        group = await get_object_by_id(Table=Group, id=uuid4(), session=session)


@pytest.mark.asyncio
async def test_get_object_by_id_correctly_raises_invalid_table_exception(
    user_in_db: User,
    group_in_db: Group,
    session: AsyncSession,
):
    with pytest.raises(InvalidTableException):
        smth = await get_object_by_id(Table=InvalidTable, id=uuid4(), session=session)
