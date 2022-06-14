from fastapi import status
from httpx import AsyncClient, Response
import pytest

from src.apps.groups.models import Group
from src.apps.posts.models import GroupPost, GroupPostComment, GroupPostReaction
from src.apps.users.models import User


@pytest.mark.asyncio
async def test_user_can_get_group_post_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/", headers=user_bearer_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["group_id"] == str(group_post_in_db.group_id)
    assert response_body[0]["user_id"] == str(group_post_in_db.user_id)
    assert response_body[0]["text"] == group_post_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["group_id"] == str(group_post_in_db.group_id)
    assert response_body[0]["user_id"] == str(group_post_in_db.user_id)
    assert response_body[0]["text"] == group_post_in_db.text


@pytest.mark.asyncio
async def test_user_can_get_group_post_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["group_id"] == str(group_post_in_db.group_id)
    assert response_body["user_id"] == str(group_post_in_db.user_id)
    assert response_body["text"] == group_post_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["group_id"] == str(group_post_in_db.group_id)
    assert response_body["user_id"] == str(group_post_in_db.user_id)
    assert response_body["text"] == group_post_in_db.text


@pytest.mark.asyncio
async def test_not_a_member_cannot_get_closed_group_post_by_id(
    client: AsyncClient,
    closed_group_in_db: Group,
    group_post_in_db: GroupPost,
    other_user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{closed_group_in_db.id}/posts/{group_post_in_db.id}/",
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_closed_group_post_by_id(
    client: AsyncClient,
    closed_group_in_db: Group,
    group_post_in_db: GroupPost,
):
    response = await client.get(
        f"/groups/{closed_group_in_db.id}/posts/{group_post_in_db.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_create_user_post(
    client: AsyncClient,
    post_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    user_bearer_token_header: dict[str, str],
):

    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/",
        json=post_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_body = response.json()
    assert response_body["group_id"] == str(public_group_in_db.id)
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["text"] == post_data["text"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_create_user_post(
    client: AsyncClient,
    post_data: dict[str, str],
    public_group_in_db: Group,
):

    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/",
        json=post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_user_can_update_user_post(
    client: AsyncClient,
    post_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    user_bearer_token_header: dict[str, str],
):

    response = await client.put(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
        json=post_update_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["group_id"] == str(public_group_in_db.id)
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["text"] == post_update_data["text"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_update_user_post(
    client: AsyncClient,
    post_update_data: dict[str, str],
    group_post_in_db: GroupPost,
    public_group_in_db: Group,
):

    response = await client.put(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
        json=post_update_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_user_can_delete_user_post(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    user_bearer_token_header: dict[str, str],
):

    response = await client.delete(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_anonymous_user_cannot_delete_user_post(
    client: AsyncClient,
    group_post_in_db: GroupPost,
    public_group_in_db: Group,
):

    response = await client.delete(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_body = response.json()
    assert len(response_body) == 1
    assert response_body["detail"] == "Missing Authorization Header"


@pytest.mark.asyncio
async def test_user_can_get_group_post_comment_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["post_id"] == str(group_post_comment_in_db.post_id)
    assert response_body[0]["user_id"] == str(group_post_comment_in_db.user_id)
    assert response_body[0]["text"] == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_comment_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["post_id"] == str(group_post_comment_in_db.post_id)
    assert response_body[0]["user_id"] == str(group_post_comment_in_db.user_id)
    assert response_body[0]["text"] == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_user_can_get_group_post_comment_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_comment_in_db.post_id)
    assert response_body["user_id"] == str(group_post_comment_in_db.user_id)
    assert response_body["text"] == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_comment_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_comment_in_db.post_id)
    assert response_body["user_id"] == str(group_post_comment_in_db.user_id)
    assert response_body["text"] == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_user_can_get_create_group_post_comment(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    comment_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/",
        json=comment_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_in_db.id)
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["text"] == comment_data["text"]


@pytest.mark.asyncio
async def test_not_a_member_cannot_get_create_group_post_comment(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    comment_data: dict[str, str],
    other_user_bearer_token_header: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/",
        json=comment_data,
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_create_group_post_comment(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    comment_data: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/",
        json=comment_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_update_group_post_comment(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    comment_update_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response = await client.put(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
        json=comment_update_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_comment_in_db.post_id)
    assert response_body["user_id"] == str(group_post_comment_in_db.user_id)
    assert response_body["text"] == comment_update_data["text"]


@pytest.mark.asyncio
async def test_anonymous_user_cannot_update_group_post_comment(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    comment_data: dict[str, str],
):
    response = await client.put(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
        json=comment_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_delete_group_post_comment(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    user_bearer_token_header: dict[str, str],
):
    response = await client.delete(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_anonymous_user_cannot_delete_group_post_comment(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
):
    response = await client.put(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/comments/{group_post_comment_in_db.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_get_group_post_reaction_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["post_id"] == str(group_post_reaction_in_db.post_id)
    assert response_body[0]["user_id"] == str(group_post_reaction_in_db.user_id)
    assert response_body[0]["reaction"] == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_reaction_list(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body[0]["post_id"] == str(group_post_reaction_in_db.post_id)
    assert response_body[0]["user_id"] == str(group_post_reaction_in_db.user_id)
    assert response_body[0]["reaction"] == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_user_can_get_group_post_reaction_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    user_bearer_token_header: dict[str, str],
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/{group_post_reaction_in_db.id}/",
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_reaction_in_db.post_id)
    assert response_body["user_id"] == str(group_post_reaction_in_db.user_id)
    assert response_body["reaction"] == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_anonymous_user_can_get_group_post_reaction_by_id(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
):
    response = await client.get(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/{group_post_reaction_in_db.id}/",
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_reaction_in_db.post_id)
    assert response_body["user_id"] == str(group_post_reaction_in_db.user_id)
    assert response_body["reaction"] == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_user_can_get_create_group_post_reaction(
    client: AsyncClient,
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    reaction_data: dict[str, str],
    user_bearer_token_header: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/",
        json=reaction_data,
        headers=user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_body = response.json()
    assert response_body["post_id"] == str(group_post_in_db.id)
    assert response_body["user_id"] == str(user_in_db.id)
    assert response_body["reaction"] == reaction_data["reaction"]


@pytest.mark.asyncio
async def test_not_a_member_cannot_get_create_group_post_reaction(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    reaction_data: dict[str, str],
    other_user_bearer_token_header: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/",
        json=reaction_data,
        headers=other_user_bearer_token_header,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_create_group_post_reaction(
    client: AsyncClient,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    reaction_data: dict[str, str],
):
    response = await client.post(
        f"/groups/{public_group_in_db.id}/posts/{group_post_in_db.id}/reactions/",
        json=reaction_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
