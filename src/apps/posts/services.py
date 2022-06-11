from typing import Union
from uuid import UUID
from sqlmodel import select, update, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.posts.models import (
    GroupPost,
    GroupPostComment,
    GroupPostReaction,
    UserPost,
    UserPostComment,
    UserPostReaction,
)

from src.core.exceptions import (
    AlreadyExistsException,
    PermissionDeniedException,
    DoesNotExistException,
)

from src.apps.users.models import User
from src.core.utils import get_object_by_id


class UserPostService:

    # --- --- Posts --- ---

    @classmethod
    async def filter_get_user_posts(
        session: AsyncSession,
    ) -> list[UserPost]:
        ...

    @classmethod
    async def filter_get_user_post_by_id(
        session: AsyncSession,
    ) -> UserPost:
        ...

    @classmethod
    async def create_user_post(
        session: AsyncSession,
    ) -> UserPost:
        ...

    @classmethod
    async def update_user_post(
        session: AsyncSession,
    ) -> UserPost:
        ...

    @classmethod
    async def delete_user_post(
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_user_post_comments(
        session: AsyncSession,
    ) -> list[UserPostComment]:
        ...

    @classmethod
    async def filter_get_user_post_comment_by_id(
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def create_user_post_comment(
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def update_user_post_comment(
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def delete_user_post_comment(
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_user_post_reactions(
        session: AsyncSession,
    ) -> list[UserPostReaction]:
        ...

    @classmethod
    async def filter_get_user_post_reaction_by_id(
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def create_user_post_reaction(
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def update_user_post_reaction(
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def delete_user_post_reaction(
        session: AsyncSession,
    ) -> None:
        ...


class GroupPostService:

    # --- --- Posts --- ---

    @classmethod
    async def filter_get_group_posts(
        session: AsyncSession,
    ) -> list[GroupPost]:
        ...

    @classmethod
    async def filter_get_group_post_by_id(
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def create_group_post(
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def update_group_post(
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def delete_group_post(
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_group_post_comments(
        session: AsyncSession,
    ) -> list[GroupPostComment]:
        ...

    @classmethod
    async def filter_get_group_post_comment_by_id(
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def create_group_post_comment(
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def update_group_post_comment(
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def delete_group_post_comment(
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_group_post_reactions(
        session: AsyncSession,
    ) -> list[GroupPostReaction]:
        ...

    @classmethod
    async def filter_get_group_post_reaction_by_id(
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def create_group_post_reaction(
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def update_group_post_reaction(
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def delete_group_post_reaction(
        session: AsyncSession,
    ) -> None:
        ...
