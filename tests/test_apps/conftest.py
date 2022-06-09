import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_another_jwt_auth import AuthJWT
from src.apps.groups.models import (
    Group,
    GroupInputSchema,
    GroupMembership,
    GroupOutputSchema,
    GroupRequest,
)
from src.apps.groups.services import GroupService

from src.apps.users.services import UserService
from src.apps.users.models import (
    Friend,
    FriendRequest,
    User,
    UserOutputSchema,
    RegisterSchema,
)


# Users


@pytest.fixture
def user_register_data() -> dict[str, str]:
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
    user_register_data: dict[str, str], session: AsyncSession
) -> UserOutputSchema:
    schema = RegisterSchema(**user_register_data)
    return await UserService.register_user(schema=schema, session=session)


@pytest.fixture
def user_bearer_token_header(user_in_db: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(subject=user_in_db.json())
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def other_user_register_data() -> dict[str, str]:
    return {
        "first_name": "name2",
        "last_name": "name2",
        "username": "username2",
        "email": "testuser2@google.com",
        "password": "test12345",
        "password2": "test12345",
        "birthday": "2000-01-01",
    }


@pytest_asyncio.fixture
async def other_user_in_db(
    other_user_register_data: dict[str, str], session: AsyncSession
) -> UserOutputSchema:
    schema = RegisterSchema(**other_user_register_data)
    return await UserService.register_user(schema=schema, session=session)


@pytest.fixture
def other_user_bearer_token_header(
    other_user_in_db: UserOutputSchema,
) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(subject=other_user_in_db.json())
    return {"Authorization": f"Bearer {access_token}"}


# Groups


@pytest.fixture
def group_create_data() -> dict[str, str]:
    return {
        "name": "test name",
        "description": "description",
        "status": "PUBLIC",
    }


@pytest_asyncio.fixture
async def public_group_in_db(
    group_create_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
) -> GroupOutputSchema:
    schema = GroupInputSchema(**group_create_data)
    return await GroupService.create_group(
        schema=schema, user=user_in_db, session=session
    )


@pytest_asyncio.fixture
async def private_group_in_db(
    group_create_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
) -> GroupOutputSchema:
    schema = GroupInputSchema(**group_create_data)
    schema.name = "test private"
    schema.status = "PRIVATE"
    return await GroupService.create_group(
        schema=schema, user=user_in_db, session=session
    )


@pytest_asyncio.fixture
async def closed_group_in_db(
    group_create_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
) -> GroupOutputSchema:
    schema = GroupInputSchema(**group_create_data)
    schema.name = "test closed"
    schema.status = "CLOSED"
    return await GroupService.create_group(
        schema=schema, user=user_in_db, session=session
    )


@pytest.fixture
def group_update_data() -> dict[str, str]:
    return {
        "name": "updated name",
        "description": "description",
        "status": "PRIVATE",
    }


@pytest_asyncio.fixture
async def group_request_in_db(
    other_user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
) -> GroupRequest:
    request = GroupRequest(
        group=public_group_in_db, user=other_user_in_db, status="PENDING"
    )
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request


@pytest_asyncio.fixture
async def group_membership_in_db(
    other_user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
) -> GroupMembership:
    membership = GroupMembership(
        group=public_group_in_db, user=other_user_in_db, membership_status="REGULAR"
    )
    session.add(membership)
    await session.commit()
    await session.refresh(membership)
    return membership


@pytest_asyncio.fixture
async def friends_in_db(
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
) -> tuple[Friend]:
    friend1 = Friend(user_id=user_in_db.id, friend_user_id=other_user_in_db.id)
    friend2 = Friend(user_id=other_user_in_db.id, friend_user_id=user_in_db.id)
    session.add(friend1)
    session.add(friend2)
    await session.commit()
    await session.refresh(friend1)
    await session.refresh(friend2)
    return (friend1, friend2)


@pytest_asyncio.fixture
async def friend_request_in_db(
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
) -> FriendRequest:
    friend_request = FriendRequest(
        from_user_id=user_in_db.id, to_user_id=other_user_in_db.id, status="PENDING"
    )
    session.add(friend_request)
    await session.commit()
    await session.refresh(friend_request)
    return friend_request


@pytest_asyncio.fixture
async def received_friend_request_in_db(
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
) -> FriendRequest:
    friend_request = FriendRequest(
        from_user_id=other_user_in_db.id, to_user_id=user_in_db.id, status="PENDING"
    )
    session.add(friend_request)
    await session.commit()
    await session.refresh(friend_request)
    return friend_request
