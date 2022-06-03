from fastapi import Response, status
from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.groups.models import (
    Group,
    GroupInputSchema,
    GroupMembership,
    GroupOutputSchema,
)
from src.apps.groups.services import GroupService
from src.apps.users.models import User, UserOutputSchema


@pytest.fixture
def group_create_data() -> dict[str, str]:
    return {
        "name": "test name",
        "description": "description",
        "status": "PUBLIC",
    }


@pytest_asyncio.fixture
async def group_in_db(
    group_create_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
) -> GroupOutputSchema:
    schema = GroupInputSchema(**group_create_data)
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


@pytest.mark.asyncio
async def test_authenticated_user_can_create_group(
    client: AsyncClient,
    group_create_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
    session: AsyncSession,
):
    response: Response = await client.post(
        "/groups/", json=group_create_data, headers=user_bearer_token_header
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len((await session.exec(select(Group))).all()) == 1
    assert (await session.exec(select(Group))).first().name == group_create_data["name"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_create_group(
    client: AsyncClient,
    group_create_data: dict[str, str],
    session: AsyncSession,
):
    response: Response = await client.post("/groups/", json=group_create_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_authenticated_user_can_update_group(
    client: AsyncClient,
    group_in_db: Group,
    group_update_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
    session: AsyncSession,
):
    print((await session.exec(select(User))).all())
    print((await session.exec(select(GroupMembership))).all())
    print(user_bearer_token_header)
    response: Response = await client.put(
        f"/groups/{group_in_db.id}/",
        json=group_update_data,
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len((await session.exec(select(Group))).all()) == 1
    assert (await session.exec(select(Group))).first().name == group_update_data["name"]
