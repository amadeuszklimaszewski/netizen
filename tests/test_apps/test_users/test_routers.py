from fastapi import status
from httpx import AsyncClient, Response
import pytest

from src.apps.users.models import User


@pytest.fixture
def user_login_data() -> dict[str, str]:
    return {
        "email": "testuser@google.com",
        "password": "test12345",
    }


@pytest.mark.asyncio
async def test_user_can_login(
    client: AsyncClient,
    user_in_db: User,
    user_login_data: dict[str, str],
):
    response: Response = await client.post("/users/login/", json=user_login_data)

    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_user_can_register(
    client: AsyncClient,
    user_register_data: dict[str, str],
):
    response: Response = await client.post("/users/register/", json=user_register_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_body = response.json()
    assert response_body["username"] == user_register_data["username"]


@pytest.mark.asyncio
async def test_authenticated_user_can_get_users_list(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get("/users/", headers=user_bearer_token_header)
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_authenticated_user_can_get_his_profile(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        "/users/profile/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["username"] == user_in_db.username
    assert response_body["id"] == str(user_in_db.id)


@pytest.mark.asyncio
async def test_authenticated_user_can_get_his_profile_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["username"] == user_in_db.username
    assert response_body["id"] == str(user_in_db.id)


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_users_list(
    client: AsyncClient,
    user_in_db: User,
):
    response: Response = await client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_users_profile(
    client: AsyncClient,
    user_in_db: User,
):
    response: Response = await client.get("/users/profile/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_users_profile_by_id(
    client: AsyncClient,
    user_in_db: User,
):
    response: Response = await client.get(f"/users/{user_in_db.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"
