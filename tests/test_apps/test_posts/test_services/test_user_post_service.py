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
    posts = await UserPostService.filter_get_user_post_list(
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


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_user_post_by_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    post = await UserPostService.filter_get_user_post_by_id(
        user_id=user_in_db.id, post_id=user_post_in_db.id, session=session
    )
    assert post.user_id == user_in_db.id
    assert post.text == user_post_in_db.text


@pytest.mark.asyncio
async def test_filter_user_post_by_id_raises_exception_with_wrong_user_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        post = await UserPostService.filter_get_user_post_by_id(
            user_id=uuid4(), post_id=user_post_in_db.id, session=session
        )


@pytest.mark.asyncio
async def test_filter_user_post_by_id_raises_exception_with_wrong_post_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        post = await UserPostService.filter_get_user_post_by_id(
            user_id=user_in_db.id, post_id=uuid4(), session=session
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_updates_post(
    post_update_data: dict[str, str],
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_update_data)
    post = await UserPostService.update_user_post(
        schema=schema,
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert post.user_id == user_in_db.id
    assert post.text == post_update_data["text"]

    result = (await session.exec(select(UserPost))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].text == post_update_data["text"]


@pytest.mark.asyncio
async def test_update_user_post_raises_exception_with_wrong_request_user(
    post_update_data: dict[str, str],
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_update_data)
    with pytest.raises(PermissionDeniedException):
        post = await UserPostService.update_user_post(
            schema=schema,
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_deletes_post(
    post_update_data: dict[str, str],
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_update_data)
    post = await UserPostService.delete_user_post(
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )

    result = (await session.exec(select(UserPost))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_user_post_raises_exception_with_wrong_request_user(
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        post = await UserPostService.delete_user_post(
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )