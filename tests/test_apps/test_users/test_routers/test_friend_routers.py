from fastapi import status
from httpx import AsyncClient, Response
import pytest

from src.apps.users.models import User, Friend, FriendRequest


@pytest.mark.asyncio
async def test_user_can_send_friend_request(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
):
    response: Response = await client.post(
        f"/users/{other_user_in_db.id}/add-friend/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()
    assert response_body["from_user_id"] == str(user_in_db.id)
    assert response_body["to_user_id"] == str(other_user_in_db.id)


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_users_list(
    client: AsyncClient,
    user_in_db: User,
    other_user_in_db: User,
):
    response: Response = await client.post(f"/users/{other_user_in_db.id}/add-friend/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_user_can_get_friend_list(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
):
    response: Response = await client.get(
        "/users/profile/friends/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body[0]["user_id"] == str(user_in_db.id)
    assert response_body[0]["friend_user_id"] == str(other_user_in_db.id)


@pytest.mark.asyncio
async def test_user_can_get_friend_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
):
    response: Response = await client.get(
        f"/users/profile/friends/{friends_in_db[0].id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["friend_user_id"] == str(other_user_in_db.id)


@pytest.mark.asyncio
async def test_user_can_get_received_friend_requests_list(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    received_friend_request_in_db: FriendRequest,
):
    response: Response = await client.get(
        "/users/profile/requests/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body[0]["to_user_id"] == str(
        received_friend_request_in_db.to_user_id
    )
    assert response_body[0]["from_user_id"] == str(
        received_friend_request_in_db.from_user_id
    )
    assert response_body[0]["status"] == received_friend_request_in_db.status


@pytest.mark.asyncio
async def test_user_can_get_sent_friend_requests_list(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    friend_request_in_db: FriendRequest,
):
    response: Response = await client.get(
        "/users/profile/requests/sent/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body[0]["from_user_id"] == str(friend_request_in_db.from_user_id)
    assert response_body[0]["to_user_id"] == str(friend_request_in_db.to_user_id)
    assert response_body[0]["status"] == friend_request_in_db.status


@pytest.mark.asyncio
async def test_user_can_get_received_friend_request_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    received_friend_request_in_db: FriendRequest,
):
    response: Response = await client.get(
        f"/users/profile/requests/{received_friend_request_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body["to_user_id"] == str(received_friend_request_in_db.to_user_id)
    assert response_body["from_user_id"] == str(
        received_friend_request_in_db.from_user_id
    )
    assert response_body["status"] == received_friend_request_in_db.status


@pytest.mark.asyncio
async def test_user_can_get_received_friend_request_by_id(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    other_user_in_db: User,
    friend_request_in_db: FriendRequest,
):
    response: Response = await client.get(
        f"/users/profile/requests/sent/{friend_request_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK

    response_body = response.json()
    assert response_body["to_user_id"] == str(friend_request_in_db.to_user_id)
    assert response_body["from_user_id"] == str(friend_request_in_db.from_user_id)
    assert response_body["status"] == friend_request_in_db.status


@pytest.mark.asyncio
async def test_user_can_delete_friend(
    client: AsyncClient,
    user_in_db: User,
    friends_in_db: list[Friend],
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/profile/friends/{friends_in_db[0].id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_user_cannot_delete_invalid_friend(
    client: AsyncClient,
    user_in_db: User,
    friends_in_db: list[Friend],
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/profile/friends/{friends_in_db[1].id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_delete_friend_request(
    client: AsyncClient,
    user_in_db: User,
    friend_request_in_db: FriendRequest,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/profile/requests/sent/{friend_request_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_other_user_cannot_delete_friend_request(
    client: AsyncClient,
    user_in_db: User,
    friend_request_in_db: FriendRequest,
    other_user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/profile/requests/sent/{friend_request_in_db.id}/",
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_can_update_received_friend_request(
    client: AsyncClient,
    user_in_db: User,
    user_bearer_token_header: dict[str, str],
    received_friend_request_in_db: FriendRequest,
):
    update_data = {"status": "ACCEPTED"}
    response: Response = await client.put(
        f"/users/profile/requests/{received_friend_request_in_db.id}/",
        json=update_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
