from uuid import UUID, uuid4
import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.groups.models import Group

from src.apps.posts.models import (
    GroupPost,
    GroupPostComment,
    GroupPostReaction,
)
from src.apps.posts.schemas import (
    PostInputSchema,
    CommentInputSchema,
    ReactionInputSchema,
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
async def test_group_post_service_correctly_creates_post(
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
    await GroupPostService.delete_group_post(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )

    result = (await session.exec(select(GroupPost))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_post_comment_list(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    comments = await GroupPostService.filter_get_group_post_comment_list(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert len(comments) == 1
    assert comments[0].post_id == group_post_in_db.id
    assert comments[0].user_id == user_in_db.id
    assert comments[0].text == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_post_comment_by_id(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    comment = await GroupPostService.filter_get_group_post_comment_by_id(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        comment_id=group_post_comment_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert comment.post_id == group_post_in_db.id
    assert comment.user_id == user_in_db.id
    assert comment.text == group_post_comment_in_db.text


@pytest.mark.asyncio
async def test_filter_post_comment_by_id_raises_exceptions_with_invalid_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.filter_get_group_post_comment_by_id(
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.filter_get_group_post_comment_by_id(
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.filter_get_group_post_comment_by_id(
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            comment_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_creates_post_comment(
    comment_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = CommentInputSchema(**comment_data)
    comment = await GroupPostService.create_group_post_comment(
        schema=schema,
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert comment.user_id == user_in_db.id
    assert comment.post_id == group_post_in_db.id
    assert comment.text == comment_data["text"]

    result = (await session.exec(select(GroupPostComment))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == group_post_in_db.id
    assert result[0].text == comment_data["text"]


@pytest.mark.asyncio
async def test_create_post_comment_raises_exception_with_invalid_post_id(
    comment_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = CommentInputSchema(**comment_data)
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.create_group_post_comment(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_updates_post_comment(
    comment_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    schema = CommentInputSchema(**comment_update_data)
    comment = await GroupPostService.update_group_post_comment(
        schema=schema,
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        comment_id=group_post_comment_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert comment.user_id == user_in_db.id
    assert comment.post_id == group_post_in_db.id
    assert comment.text == comment_update_data["text"]

    result = (await session.exec(select(GroupPostComment))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == group_post_in_db.id
    assert result[0].text == comment_update_data["text"]


@pytest.mark.asyncio
async def test_update_post_comment_raises_exceptions_with_invalid_ids(
    comment_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    schema = CommentInputSchema(**comment_update_data)
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.update_group_post_comment(
            schema=schema,
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.update_group_post_comment(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        comment = await GroupPostService.update_group_post_comment(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            comment_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_deletes_post_comment(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    await GroupPostService.delete_group_post_comment(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        comment_id=group_post_comment_in_db.id,
        request_user=user_in_db,
        session=session,
    )

    result = (await session.exec(select(GroupPostComment))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_post_comment_raises_exceptions_with_invalid_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_comment_in_db: GroupPostComment,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_comment(
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_comment(
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            comment_id=group_post_comment_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_comment(
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            comment_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_post_reaction_list(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    reactions = await GroupPostService.filter_get_group_post_reaction_list(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert len(reactions) == 1
    assert reactions[0].post_id == group_post_in_db.id
    assert reactions[0].user_id == user_in_db.id
    assert reactions[0].reaction == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_group_post_service_correctly_filters_post_reaction_by_id(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    reaction = await GroupPostService.filter_get_group_post_reaction_by_id(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        reaction_id=group_post_reaction_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert reaction.post_id == group_post_in_db.id
    assert reaction.user_id == user_in_db.id
    assert reaction.reaction == group_post_reaction_in_db.reaction


@pytest.mark.asyncio
async def test_filter_post_reaction_by_id_raises_exceptions_with_invalid_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.filter_get_group_post_reaction_by_id(
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.filter_get_group_post_reaction_by_id(
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.filter_get_group_post_reaction_by_id(
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            reaction_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_creates_post_reaction(
    reaction_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_data)
    reaction = await GroupPostService.create_group_post_reaction(
        schema=schema,
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert reaction.user_id == user_in_db.id
    assert reaction.post_id == group_post_in_db.id
    assert reaction.reaction == reaction_data["reaction"]

    result = (await session.exec(select(GroupPostReaction))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == group_post_in_db.id
    assert result[0].reaction == reaction_data["reaction"]


@pytest.mark.asyncio
async def test_create_post_reaction_raises_exception_with_invalid_post_id(
    reaction_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_data)
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.create_group_post_reaction(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_updates_post_reaction(
    reaction_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_update_data)
    reaction = await GroupPostService.update_group_post_reaction(
        schema=schema,
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        reaction_id=group_post_reaction_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert reaction.user_id == user_in_db.id
    assert reaction.post_id == group_post_in_db.id
    assert reaction.reaction == reaction_update_data["reaction"]

    result = (await session.exec(select(GroupPostReaction))).all()
    assert len(result) == 1
    assert result[0].user_id == user_in_db.id
    assert result[0].post_id == group_post_in_db.id
    assert result[0].reaction == reaction_update_data["reaction"]


@pytest.mark.asyncio
async def test_update_post_reaction_raises_exceptions_with_invalid_ids(
    reaction_update_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    schema = ReactionInputSchema(**reaction_update_data)
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.update_group_post_reaction(
            schema=schema,
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.update_group_post_reaction(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        reaction = await GroupPostService.update_group_post_reaction(
            schema=schema,
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            reaction_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_group_post_service_correctly_deletes_post_reaction(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    await GroupPostService.delete_group_post_reaction(
        group_id=public_group_in_db.id,
        post_id=group_post_in_db.id,
        reaction_id=group_post_reaction_in_db.id,
        request_user=user_in_db,
        session=session,
    )

    result = (await session.exec(select(GroupPostReaction))).all()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_post_reaction_raises_exceptions_with_invalid_ids(
    user_in_db: User,
    public_group_in_db: Group,
    group_post_in_db: GroupPost,
    group_post_reaction_in_db: GroupPostReaction,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_reaction(
            group_id=uuid4(),
            post_id=group_post_in_db.id,
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_reaction(
            group_id=public_group_in_db.id,
            post_id=uuid4(),
            reaction_id=group_post_reaction_in_db.id,
            request_user=user_in_db,
            session=session,
        )
    with pytest.raises(DoesNotExistException):
        await GroupPostService.delete_group_post_reaction(
            group_id=public_group_in_db.id,
            post_id=group_post_in_db.id,
            reaction_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )
