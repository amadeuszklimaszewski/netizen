from fastapi import status
from httpx import AsyncClient, Response, head
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
