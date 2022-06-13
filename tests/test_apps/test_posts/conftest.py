import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.groups.models import Group

from src.apps.users.models import User
from src.apps.posts.models import (
    GroupPost,
    GroupPostComment,
    GroupPostReaction,
    UserPost,
    UserPostComment,
    UserPostReaction,
)


@pytest.fixture
def post_data() -> dict[str, str]:
    return {"text": "test post"}


@pytest.fixture
def post_update_data() -> dict[str, str]:
    return {"text": "test update"}


@pytest_asyncio.fixture
async def user_post_in_db(
    post_data: dict[str, str],
    user_in_db: User,
    session: AsyncSession,
):
    post = UserPost(**post_data, user_id=user_in_db.id)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@pytest_asyncio.fixture
async def group_post_in_db(
    post_data: dict[str, str],
    user_in_db: User,
    public_group_in_db: Group,
    session: AsyncSession,
):
    post = GroupPost(**post_data, user_id=user_in_db.id, group_id=public_group_in_db.id)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@pytest.fixture
def comment_data() -> dict[str, str]:
    return {"text": "test post"}


@pytest.fixture
def comment_update_data() -> dict[str, str]:
    return {"text": "test update"}


@pytest_asyncio.fixture
async def user_post_comment_in_db(
    comment_data: dict[str, str],
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    comment = UserPostComment(
        **comment_data, user_id=user_in_db.id, post_id=user_post_in_db.id
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@pytest_asyncio.fixture
async def group_post_comment_in_db(
    comment_data: dict[str, str],
    user_in_db: User,
    group_post_in_db: GroupPost,
    session: AsyncSession,
):
    comment = GroupPostComment(
        **comment_data, user_id=user_in_db.id, post_id=group_post_in_db.id
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@pytest.fixture
def reaction_data() -> dict[str, str]:
    return {"reaction": "LIKE"}


@pytest.fixture
def reaction_update_data() -> dict[str, str]:
    return {"reaction": "DISLIKE"}


@pytest_asyncio.fixture
async def user_post_reaction_in_db(
    reaction_data: dict[str, str],
    user_in_db: User,
    user_post_in_db: UserPost,
    session: AsyncSession,
):
    reaction = UserPostReaction(
        **reaction_data, user_id=user_in_db.id, post_id=user_post_in_db.id
    )
    session.add(reaction)
    await session.commit()
    await session.refresh(reaction)
    return reaction


@pytest_asyncio.fixture
async def group_post_reaction_in_db(
    reaction_data: dict[str, str],
    user_in_db: User,
    group_post_in_db: UserPost,
    session: AsyncSession,
):
    reaction = GroupPostReaction(
        **reaction_data, user_id=user_in_db.id, post_id=group_post_in_db.id
    )
    session.add(reaction)
    await session.commit()
    await session.refresh(reaction)
    return reaction
