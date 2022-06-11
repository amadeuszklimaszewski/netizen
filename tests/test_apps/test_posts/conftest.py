import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.users.models import User
from src.apps.posts.models import UserPost


@pytest.fixture
def post_data() -> dict[str, str]:
    return {"text": "test post"}


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
