from uuid import UUID, uuid4
import pytest
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.groups.models import Group

from src.apps.posts.models import (
    GroupPost,
    PostInputSchema,
    UserPost,
)
from src.apps.posts.services import GroupPostService
from src.apps.users.models import User
from src.core.exceptions import DoesNotExistException, PermissionDeniedException


@pytest.mark.asyncio
async def test_validate_user_access_on_get_raises_exception_with_closed_group(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        posts = await GroupPostService._validate_user_access_on_get(
            group_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_get(
            group_id=private_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_get(
            group_id=private_group_in_db.id,
            request_user=None,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_get(
            group_id=closed_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_get(
            group_id=closed_group_in_db.id,
            request_user=None,
            session=session,
        )


@pytest.mark.asyncio
async def test_validate_user_access_on_post_put_delete(
    user_in_db: User,
    other_user_in_db: User,
    public_group_in_db: Group,
    private_group_in_db: Group,
    closed_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=public_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=public_group_in_db.id,
            request_user=None,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=private_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=private_group_in_db.id,
            request_user=None,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=closed_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
    with pytest.raises(PermissionDeniedException):
        posts = await GroupPostService._validate_user_access_on_post_put_delete(
            group_id=closed_group_in_db.id,
            request_user=None,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_post_list(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    posts = await GroupPostService.filter_get_group_post_list(
        group_id=public_group_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert len(posts) == 1
    assert posts[0].group_id == public_group_in_db.id
    assert posts[0].user_id == user_in_db.id
    assert posts[0].text == group_post_in_db.text


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_user_post_by_id(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    post = await GroupPostService.filter_get_group_post_by_id(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert post.group_id == public_group_in_db.id
    assert post.text == group_post_in_db.text


@pytest.mark.asyncio
async def test_filter_group_post_list_raises_exception_with_wrong_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        post = await GroupPostService.filter_get_group_post_list(
            group_id=uuid4(), request_user=user_in_db, session=session
        )


@pytest.mark.asyncio
async def test_filter_group_post_by_id_raises_exception_with_wrong_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        post = await GroupPostService.filter_get_group_post_by_id(
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        post = await GroupPostService.filter_get_group_post_by_id(
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_creates_post(
    post_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    post = await GroupPostService.create_group_post(
        schema=schema,
        group_id=public_group_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert post.user_id == user_in_db.id
    assert post.group_id == public_group_in_db.id
    assert post.text == post_data["text"]

    result = (await session.exec(select(GroupPost))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].group_id == public_group_in_db.id
    assert result[0].text == post_data["text"]


@pytest.mark.asyncio
async def test_create_user_post_raises_exception_with_invalid_group_id(
    post_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    with pytest.raises(DoesNotExistException):
        post = await GroupPostService.create_group_post(
            schema=schema,
            group_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_create_group_post_raises_exception_with_invalid_request_user(
    post_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    other_user_in_db: User,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_data)
    with pytest.raises(PermissionDeniedException):
        post = await GroupPostService.create_group_post(
            schema=schema,
            group_id=public_group_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_updates_post(
    post_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_update_data)
    post = await GroupPostService.update_group_post(
        schema=schema,
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert post.user_id == user_in_db.id
    assert post.group_id == public_group_in_db.id
    assert post.text == post_update_data["text"]

    result = (await session.exec(select(GroupPost))).all()

    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].group_id == public_group_in_db.id
    assert result[0].text == post_update_data["text"]


@pytest.mark.asyncio
async def test_group_post_service_correctly_deletes_post(
    post_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = PostInputSchema(**post_update_data)
    post = await GroupPostService.delete_group_post(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )

    result = (await session.exec(select(GroupPost))).all()
    assert len(result) == 0
