from fastapi import status
from httpx import AsyncClient, Response
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.apps.groups.models import (
    Group,
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
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    public_group_in_db: Group,
):
    response: Response = await client.post(
        f"/groups/{public_group_in_db.id}/join/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()
    assert response_body["group_id"] == str(public_group_in_db.id)
    assert response_body["user_id"] == str(user_in_db.id)
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
