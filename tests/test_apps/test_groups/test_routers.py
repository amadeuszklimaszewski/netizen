from fastapi import status
from httpx import AsyncClient, Response
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update
from sqlalchemy import and_
from src.apps.groups.models import (
    Group,
    GroupMembership,
    GroupRequest,
)
from src.apps.users.models import User


@pytest.mark.asyncio
async def test_authenticated_user_can_get_groups_list(
    client: AsyncSession,
    public_group_in_db: Group,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get("/groups/", headers=user_bearer_token_header)
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 1
    assert response_body[0]["name"] == public_group_in_db.name
    assert response_body[0]["description"] == public_group_in_db.description
    assert response_body[0]["status"] == public_group_in_db.status


@pytest.mark.asyncio
async def test_anonymous_user_can_get_groups_list(
    client: AsyncSession,
    public_group_in_db: Group,
):
    response: Response = await client.get("/groups/")
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 1
    assert response_body[0]["name"] == public_group_in_db.name
    assert response_body[0]["description"] == public_group_in_db.description
    assert response_body[0]["status"] == public_group_in_db.status


@pytest.mark.asyncio
async def test_authenticated_user_can_get_group_by_id(
    client: AsyncSession,
    public_group_in_db: Group,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["name"] == public_group_in_db.name
    assert response_body["description"] == public_group_in_db.description
    assert response_body["status"] == public_group_in_db.status


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_by_id(
    client: AsyncSession,
    public_group_in_db: Group,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(f"/groups/{public_group_in_db.id}/")
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["name"] == public_group_in_db.name
    assert response_body["description"] == public_group_in_db.description
    assert response_body["status"] == public_group_in_db.status


@pytest.mark.asyncio
async def test_authenticated_user_can_create_group(
    client: AsyncClient,
    group_create_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.post(
        "/groups/", json=group_create_data, headers=user_bearer_token_header
    )

    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()
    assert response_body["name"] == group_create_data["name"]
    assert response_body["description"] == group_create_data["description"]
    assert response_body["status"] == group_create_data["status"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_create_group(
    client: AsyncClient,
    group_create_data: dict[str, str],
):
    response: Response = await client.post("/groups/", json=group_create_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_admin_can_update_group(
    client: AsyncClient,
    public_group_in_db: Group,
    group_update_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.put(
        f"/groups/{public_group_in_db.id}/",
        json=group_update_data,
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["name"] == group_update_data["name"]
    assert response_body["description"] == group_update_data["description"]
    assert response_body["status"] == group_update_data["status"]


@pytest.mark.asyncio
async def test_regular_user_cannot_update_group(
    client: AsyncClient,
    other_user_bearer_token_header: dict[str, str],
    public_group_in_db: Group,
    group_update_data: dict[str, str],
):

    response: Response = await client.put(
        f"/groups/{public_group_in_db.id}/",
        json=group_update_data,
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_anonymous_user_cannot_update_group(
    client: AsyncClient,
    public_group_in_db: Group,
    group_update_data: dict[str, str],
):
    response: Response = await client.put(
        f"/groups/{public_group_in_db.id}/", json=group_update_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_admin_can_delete_group(
    client: AsyncClient,
    public_group_in_db: Group,
    group_update_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/groups/{public_group_in_db.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_anonymous_user_cannot_delete_group(
    client: AsyncClient,
    public_group_in_db: Group,
    group_update_data: dict[str, str],
):
    response: Response = await client.delete(f"/groups/{public_group_in_db.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_authenticated_user_can_request_to_join_group(
    client: AsyncClient,
    other_user_in_db: User,
    other_user_bearer_token_header: dict[str, str],
    public_group_in_db: Group,
):
    response: Response = await client.post(
        f"/groups/{public_group_in_db.id}/join/",
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()
    assert response_body["group_id"] == str(public_group_in_db.id)
    assert response_body["user_id"] == str(other_user_in_db.id)
    assert response_body["status"] == "PENDING"


@pytest.mark.asyncio
async def test_anonymous_user_cannot_request_to_join_group(
    client: AsyncClient,
    public_group_in_db: Group,
):
    response: Response = await client.post(
        f"/groups/{public_group_in_db.id}/join/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_authenticated_user_can_leave_group(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    public_group_in_db: Group,
):
    response: Response = await client.delete(
        f"/groups/{public_group_in_db.id}/leave/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_anonymous_user_cannot_leave_group(
    client: AsyncClient,
    public_group_in_db: Group,
):
    response: Response = await client.delete(
        f"/groups/{public_group_in_db.id}/leave/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_admin_user_can_get_group_request_list(
    client: AsyncSession,
    user_bearer_token_header: dict[str, str],
    group_request_in_db: GroupRequest,
    public_group_in_db: Group,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/requests/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 1
    assert response_body[0]["group_id"] == str(group_request_in_db.group_id)
    assert response_body[0]["user_id"] == str(group_request_in_db.user_id)
    assert response_body[0]["status"] == group_request_in_db.status


@pytest.mark.asyncio
async def test_regular_user_cannot_get_group_request_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    await session.execute(
        update(GroupMembership)
        .where(
            and_(
                GroupMembership.group_id == public_group_in_db.id,
                GroupMembership.user_id == user_in_db.id,
            )
        )
        .values(membership_status="REGULAR")
    )
    response: Response = await client.get(f"/groups/{public_group_in_db.id}/requests/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_group_request_list(
    client: AsyncClient,
    public_group_in_db: Group,
):
    response: Response = await client.get(f"/groups/{public_group_in_db.id}/requests/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_admin_user_can_get_group_request_by_id(
    client: AsyncSession,
    user_bearer_token_header: dict[str, str],
    group_request_in_db: GroupRequest,
    public_group_in_db: Group,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/requests/{group_request_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["group_id"] == str(group_request_in_db.group_id)
    assert response_body["user_id"] == str(group_request_in_db.user_id)
    assert response_body["status"] == group_request_in_db.status


@pytest.mark.asyncio
async def test_regular_user_cannot_get_group_request_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
    session: AsyncSession,
):
    await session.execute(
        update(GroupMembership)
        .where(
            and_(
                GroupMembership.group_id == public_group_in_db.id,
                GroupMembership.user_id == user_in_db.id,
            )
        )
        .values(membership_status="REGULAR")
    )
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/requests/{group_request_in_db.id}/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_group_request_by_id(
    client: AsyncClient,
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/requests/{group_request_in_db.id}/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_admin_user_can_update_request(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    public_group_in_db: Group,
    group_request_in_db: GroupRequest,
):
    update_data = {"status": "ACCEPTED"}
    response: Response = await client.put(
        f"/groups/{public_group_in_db.id}/requests/{group_request_in_db.id}/",
        json=update_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["status"] == "ACCEPTED"
    assert response_body["user_id"] == str(group_request_in_db.user_id)
    assert response_body["group_id"] == str(group_request_in_db.group_id)


@pytest.mark.asyncio
async def test_user_can_get_group_members_list(
    client: AsyncSession,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    group_membership_in_db: GroupMembership,
    public_group_in_db: Group,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/members/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 2

    assert response_body[0]["group_id"] == str(public_group_in_db.id)
    assert response_body[0]["user_id"] == str(user_in_db.id)
    assert response_body[0]["membership_status"] == "ADMIN"

    assert response_body[1]["group_id"] == str(group_membership_in_db.group_id)
    assert response_body[1]["user_id"] == str(group_membership_in_db.user_id)
    assert (
        response_body[1]["membership_status"]
        == group_membership_in_db.membership_status
    )


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_closed_group_members_list(
    client: AsyncSession,
    group_membership_in_db: GroupMembership,
    closed_group_in_db: Group,
):
    response: Response = await client.get(f"/groups/{closed_group_in_db.id}/members/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_admin_user_can_get_group_membership_by_id(
    client: AsyncSession,
    user_bearer_token_header: dict[str, str],
    group_membership_in_db: GroupMembership,
    public_group_in_db: Group,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/members/{group_membership_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["group_id"] == str(group_membership_in_db.group_id)
    assert response_body["user_id"] == str(group_membership_in_db.user_id)
    assert (
        response_body["membership_status"] == group_membership_in_db.membership_status
    )


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_membership_by_id(
    client: AsyncSession,
    group_membership_in_db: GroupMembership,
    public_group_in_db: Group,
):
    response: Response = await client.get(
        f"/groups/{public_group_in_db.id}/members/{group_membership_in_db.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()

    assert response_body["group_id"] == str(group_membership_in_db.group_id)
    assert response_body["user_id"] == str(group_membership_in_db.user_id)
    assert (
        response_body["membership_status"] == group_membership_in_db.membership_status
    )
