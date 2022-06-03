from fastapi import Response, status
from httpx import AsyncClient
import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.users.models import User, UserOutputSchema


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
    session: AsyncSession,
):
    response: Response = await client.post("/users/login/", json=user_login_data)

    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert len(response_body) == 1


@pytest.mark.asyncio
async def test_user_can_register(
    client: AsyncClient,
    user_register_data: dict[str, str],
    session: AsyncSession,
):
    response: Response = await client.post("/users/register/", json=user_register_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert len((await session.exec(select(User))).all()) == 1
    assert (await session.exec(select(User))).first().username == user_register_data[
        "username"
    ]


@pytest.mark.asyncio
async def test_authenticated_user_can_get_users_list(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    session: AsyncSession,
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
    session: AsyncSession,
):
    response: Response = await client.get(
        "/users/profile/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == user_in_db.username
    assert response.json()["id"] == str(user_in_db.id)


@pytest.mark.asyncio
async def test_authenticated_user_can_get_his_profile_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    session: AsyncSession,
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == user_in_db.username
    assert response.json()["id"] == str(user_in_db.id)


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_users_list(
    client: AsyncClient,
    user_in_db: User,
    session: AsyncSession,
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
    session: AsyncSession,
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
    session: AsyncSession,
):
    response: Response = await client.get(f"/users/{user_in_db.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"
