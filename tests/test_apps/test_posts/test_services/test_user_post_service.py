from uuid import UUID, uuid4
import pytest
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.posts.models import (
    PostInputSchema,
    ReactionInputSchema,
    UserPost,
    UserPostComment,
    UserPostReaction,
)
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
async def test_filter_user_post_list_raises_exception_with_wrong_user_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        post = await UserPostService.filter_get_user_post_list(
            user_id=uuid4(), session=session
        )


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


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_post_comment_list(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    comments = await UserPostService.filter_get_user_post_comment_list(
        user_id=user_in_db.id, post_id=user_post_in_db.id, session=session
    )
    assert len(comments) == 1
    assert comments[0].user_id == user_post_comment_in_db.user_id
    assert comments[0].post_id == user_post_comment_in_db.post_id
    assert comments[0].text == user_post_comment_in_db.text


@pytest.mark.asyncio
async def test_filter_post_comment_list_raises_exeption_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        comments = await UserPostService.filter_get_user_post_comment_list(
            user_id=uuid4(), post_id=user_post_in_db.id, session=session
        )
    with pytest.raises(DoesNotExistException):
        comments = await UserPostService.filter_get_user_post_comment_list(
            user_id=user_in_db.id, post_id=uuid4(), session=session
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_post_comment_by_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    comment = await UserPostService.filter_get_user_post_comment_by_id(
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        comment_id=user_post_comment_in_db.id,
        session=session,
    )
    assert comment.user_id == user_post_comment_in_db.user_id
    assert comment.post_id == user_post_comment_in_db.post_id
    assert comment.text == user_post_comment_in_db.text


@pytest.mark.asyncio
async def test_filter_post_comment_by_id_raises_exeption_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        comment = await UserPostService.filter_get_user_post_comment_by_id(
            user_id=uuid4(),
            post_id=user_post_in_db.id,
            comment_id=user_post_comment_in_db.id,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await UserPostService.filter_get_user_post_comment_by_id(
            user_id=user_in_db.id,
            post_id=uuid4(),
            comment_id=user_post_comment_in_db.id,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await UserPostService.filter_get_user_post_comment_by_id(
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            comment_id=uuid4(),
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_creates_post_comment(
    user_in_db: User,
    user_post_in_db: UserPost,
    comment_data: dict[str, str],
    session: AsyncSession,
):
    schema = PostInputSchema(**comment_data)
    user_post_comment = await UserPostService.create_user_post_comment(
        schema=schema,
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert user_post_comment.user_id == user_in_db.id
    assert user_post_comment.post_id == user_post_in_db.id
    assert user_post_comment.text == comment_data["text"]

    result = (await session.exec(select(UserPostComment))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == user_post_in_db.id
    assert result[0].text == comment_data["text"]


@pytest.mark.asyncio
async def test_user_post_service_correctly_updates_post_comment(
    user_in_db: User,
    user_post_in_db: UserPost,
    comment_update_data: dict[str, str],
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    schema = PostInputSchema(**comment_update_data)
    user_post_comment = await UserPostService.update_user_post_comment(
        schema=schema,
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        comment_id=user_post_comment_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert user_post_comment.user_id == user_in_db.id
    assert user_post_comment.post_id == user_post_in_db.id
    assert user_post_comment.text == comment_update_data["text"]

    result = (await session.exec(select(UserPostComment))).all()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_update_post_comment_raises_exceptions_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    comment_update_data: dict[str, str],
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    schema = PostInputSchema(**comment_update_data)
    with pytest.raises(DoesNotExistException):
        user_post_comment = await UserPostService.update_user_post_comment(
            schema=schema,
            user_id=uuid4(),
            post_id=user_post_in_db.id,
            comment_id=user_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        user_post_comment = await UserPostService.update_user_post_comment(
            schema=schema,
            user_id=user_in_db.id,
            post_id=uuid4(),
            comment_id=user_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        user_post_comment = await UserPostService.update_user_post_comment(
            schema=schema,
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            comment_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_update_post_comment_raises_exceptions_with_wrong_request_user(
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    comment_update_data: dict[str, str],
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    schema = PostInputSchema(**comment_update_data)
    with pytest.raises(PermissionDeniedException):
        user_post_comment = await UserPostService.update_user_post_comment(
            schema=schema,
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            comment_id=user_post_comment_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_deletes_post_comment(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    await UserPostService.delete_user_post_comment(
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        comment_id=user_post_comment_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    result = (await session.exec(select(UserPostComment))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_post_comment_raises_exceptions_with_wrong_request_user(
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    user_post_comment_in_db: UserPostComment,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        await UserPostService.delete_user_post_comment(
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            comment_id=user_post_comment_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_post_reaction_list(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    reactions = await UserPostService.filter_get_user_post_reaction_list(
        user_id=user_in_db.id, post_id=user_post_in_db.id, session=session
    )
    assert len(reactions) == 1
    assert reactions[0].user_id == user_post_reaction_in_db.user_id
    assert reactions[0].post_id == user_post_reaction_in_db.post_id
    assert reactions[0].reaction == user_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_filter_post_reaction_list_raises_exeption_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        reactions = await UserPostService.filter_get_user_post_reaction_list(
            user_id=uuid4(), post_id=user_post_in_db.id, session=session
        )
    with pytest.raises(DoesNotExistException):
        reactions = await UserPostService.filter_get_user_post_reaction_list(
            user_id=user_in_db.id, post_id=uuid4(), session=session
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_post_reaction_by_id(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    reaction = await UserPostService.filter_get_user_post_reaction_by_id(
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        reaction_id=user_post_reaction_in_db.id,
        session=session,
    )
    assert reaction.user_id == user_post_reaction_in_db.user_id
    assert reaction.post_id == user_post_reaction_in_db.post_id
    assert reaction.reaction == user_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_filter_post_reaction_by_id_raises_exeption_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        reaction = await UserPostService.filter_get_user_post_reaction_by_id(
            user_id=uuid4(),
            post_id=user_post_in_db.id,
            reaction_id=user_post_reaction_in_db.id,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await UserPostService.filter_get_user_post_reaction_by_id(
            user_id=user_in_db.id,
            post_id=uuid4(),
            reaction_id=user_post_reaction_in_db.id,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await UserPostService.filter_get_user_post_reaction_by_id(
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            reaction_id=uuid4(),
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_creates_post_reaction(
    user_in_db: User,
    user_post_in_db: UserPost,
    reaction_data: dict[str, str],
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_data)
    user_post_reaction = await UserPostService.create_user_post_reaction(
        schema=schema,
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert user_post_reaction.user_id == user_in_db.id
    assert user_post_reaction.post_id == user_post_in_db.id
    assert user_post_reaction.reaction == reaction_data["reaction"]

    result = (await session.exec(select(UserPostReaction))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == user_post_in_db.id
    assert result[0].reaction == reaction_data["reaction"]


@pytest.mark.asyncio
async def test_user_post_service_correctly_updates_post_reaction(
    user_in_db: User,
    user_post_in_db: UserPost,
    reaction_update_data: dict[str, str],
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_update_data)
    user_post_reaction = await UserPostService.update_user_post_reaction(
        schema=schema,
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        reaction_id=user_post_reaction_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert user_post_reaction.user_id == user_in_db.id
    assert user_post_reaction.post_id == user_post_in_db.id
    assert user_post_reaction.reaction == reaction_update_data["reaction"]

    result = (await session.exec(select(UserPostReaction))).all()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_update_post_reaction_raises_exceptions_with_wrong_ids(
    user_in_db: User,
    user_post_in_db: UserPost,
    reaction_update_data: dict[str, str],
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_update_data)
    with pytest.raises(DoesNotExistException):
        user_post_reaction = await UserPostService.update_user_post_reaction(
            schema=schema,
            user_id=uuid4(),
            post_id=user_post_in_db.id,
            reaction_id=user_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        user_post_reaction = await UserPostService.update_user_post_reaction(
            schema=schema,
            user_id=user_in_db.id,
            post_id=uuid4(),
            reaction_id=user_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        user_post_reaction = await UserPostService.update_user_post_reaction(
            schema=schema,
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            reaction_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_update_post_reaction_raises_exceptions_with_wrong_request_user(
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    reaction_update_data: dict[str, str],
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_update_data)
    with pytest.raises(PermissionDeniedException):
        user_post_reaction = await UserPostService.update_user_post_reaction(
            schema=schema,
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            reaction_id=user_post_reaction_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_user_post_service_correctly_deletes_post_reaction(
    user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    await UserPostService.delete_user_post_reaction(
        user_id=user_in_db.id,
        post_id=user_post_in_db.id,
        reaction_id=user_post_reaction_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    result = (await session.exec(select(UserPostReaction))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_post_reaction_raises_exceptions_with_wrong_request_user(
    user_in_db: User,
    other_user_in_db: User,
    user_post_in_db: UserPost,
    user_post_reaction_in_db: UserPostReaction,
    session: AsyncSession,
):
    with pytest.raises(PermissionDeniedException):
        await UserPostService.delete_user_post_reaction(
            user_id=user_in_db.id,
            post_id=user_post_in_db.id,
            reaction_id=user_post_reaction_in_db.id,
            request_user=other_user_in_db,
            session=session,
        )
