from fastapi import status
from httpx import AsyncClient, Response
import pytest
from src.apps.posts.models import UserPost

from src.apps.users.models import User


@pytest.mark.asyncio
async def test_user_can_get_user_posts_list(
    client: AsyncClient,
    user_in_db: User,
    user_post_in_db: UserPost,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/posts/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["user_id"] == str(user_post_in_db.user_id)
    assert response_body[0]["text"] == user_post_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_user_posts_list(
    client: AsyncClient,
    user_in_db: User,
    user_post_in_db: UserPost,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/posts/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["user_id"] == str(user_post_in_db.user_id)
    assert response_body[0]["text"] == user_post_in_db.text


@pytest.mark.asyncio
async def test_user_can_create_user_post(
    client: AsyncClient,
    post_data: dict[str, str],
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
):

    response: Response = await client.post(
        f"/users/{user_in_db.id}/posts/",
        json=post_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_body = response.json()
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["text"] == post_data["text"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_create_user_post(
    client: AsyncClient,
    post_data: dict[str, str],
    user_in_db: User,
):

    response: Response = await client.post(
        f"/users/{user_in_db.id}/posts/",
        json=post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_user_can_get_user_post_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_post_in_db: UserPost,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/posts/{user_post_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["user_id"] == str(user_post_in_db.user_id)
    assert response_body["text"] == user_post_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_user_post_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_post_in_db: UserPost,
):
    response: Response = await client.get(
        f"/users/{user_in_db.id}/posts/{user_post_in_db.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["user_id"] == str(user_post_in_db.user_id)
    assert response_body["text"] == user_post_in_db.text
