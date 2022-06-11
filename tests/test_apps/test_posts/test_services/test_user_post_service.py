from uuid import uuid4
import pytest
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.posts.models import UserPost
from src.apps.posts.services import UserPostService
from src.apps.users.models import User


@pytest.mark.asyncio
async def test_user_post_service_correctly_filters_postlist(
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
