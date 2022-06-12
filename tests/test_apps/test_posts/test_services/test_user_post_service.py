from uuid import uuid4
import pytest
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.posts.models import PostInputSchema, UserPost
from src.apps.posts.services import UserPostService
from src.apps.users.models import User
from src.core.exceptions import DoesNotExistException, PermissionDeniedException


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_post_list(
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    posts = await UserPostService.filter_get_user_posts(
        user_id=user_in_db.id, session=session
    )
    assert len(posts) == 1
    assert posts[0].user_id == user_in_db.id
    assert posts[0].text == user_post_in_db.text


@pytest.mark.asyncio
async def test_user_post_service_correctly_creates_post(
    post_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    post = await UserPostService.create_user_post(
        schema=schema,
        user_id=user_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert post.user_id == user_in_db.id
    assert post.text == post_data["text"]

    result = (await session.exec(select(UserPost))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].text == post_data["text"]


@pytest.mark.asyncio
async def test_create_user_post_raises_exception_with_invalid_user_id(
    post_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    with pytest.raises(DoesNotExistException):
        post = await UserPostService.create_user_post(
            schema=schema,
            user_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_create_user_post_raises_exception_with_invalid_request_user(
    post_data: dict[str, str],
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    with pytest.raises(PermissionDeniedException):
        post = await UserPostService.create_user_post(
            schema=schema,
            user_id=user_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
