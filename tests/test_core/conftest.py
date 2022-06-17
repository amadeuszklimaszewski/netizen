import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.groups.schemas import GroupInputSchema, GroupOutputSchema
from src.apps.groups.services import GroupService

from src.apps.users.services import UserService
from src.apps.users.models import User
from src.apps.users.schemas import UserOutputSchema, RegisterSchema


@pytest.fixture
def user_data() -> dict[str, str]:
    return {
        "first_name": "name",
        "last_name": "name",
        "username": "username",
        "email": "testuser@google.com",
        "password": "test12345",
        "password2": "test12345",
        "birthday": "2000-01-01",
    }


@pytest_asyncio.fixture
async def user_in_db(
    user_data: dict[str, str], session: AsyncSession
) -> UserOutputSchema:
    schema = RegisterSchema(**user_data)
    return await UserService.register_user(schema=schema, session=session)


@pytest.fixture
def group_data() -> dict[str, str]:
    return {
        "name": "test group",
        "description": "description",
        "status": "PUBLIC",
    }


@pytest_asyncio.fixture
async def group_in_db(
    group_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
) -> GroupOutputSchema:
    schema = GroupInputSchema(**group_data)
    return await GroupService.create_group(
        schema=schema, user=user_in_db, session=session
    )
