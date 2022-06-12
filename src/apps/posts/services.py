from typing import Union
from uuid import UUID
from sqlmodel import select, update, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.posts.models import (
    GroupPost,
    GroupPostComment,
    GroupPostReaction,
    PostInputSchema,
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
    async def filter_get_user_post_list(
        cls,
        user_id: UUID,
        session: AsyncSession,
    ) -> list[UserPost]:
        return (
            await session.exec(select(UserPost).where(UserPost.user_id == user_id))
        ).all()

    @classmethod
    async def filter_get_user_post_by_id(
        cls,
        user_id: UUID,
        post_id: UUID,
        session: AsyncSession,
    ) -> UserPost:
        user = await get_object_by_id(Table=User, id=user_id, session=session)
        user_post = (
            await session.exec(
                select(UserPost).where(
                    and_(
                        UserPost.user_id == user_id,
                        UserPost.id == post_id,
                    )
                )
            )
        ).first()
        if user_post is None:
            raise DoesNotExistException("User post with given id does not exist.")
        return user_post

    @classmethod
    async def create_user_post(
        cls,
        schema: PostInputSchema,
        user_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPost:
        user = await get_object_by_id(Table=User, id=user_id, session=session)
        if request_user.id != user.id:
            raise PermissionDeniedException("User unauthorized.")

        user_post_data = schema.dict()
        user_post = UserPost(**user_post_data, user_id=user_id)

        session.add(user_post)

        await session.commit()
        await session.refresh(user_post)
        return user_post

    @classmethod
    async def update_user_post(
        cls,
        session: AsyncSession,
    ) -> UserPost:
        ...

    @classmethod
    async def delete_user_post(
        cls,
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_user_post_comment_list(
        cls,
        session: AsyncSession,
    ) -> list[UserPostComment]:
        ...

    @classmethod
    async def filter_get_user_post_comment_by_id(
        cls,
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def create_user_post_comment(
        cls,
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def update_user_post_comment(
        cls,
        session: AsyncSession,
    ) -> UserPostComment:
        ...

    @classmethod
    async def delete_user_post_comment(
        cls,
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_user_post_reactions(
        cls,
        session: AsyncSession,
    ) -> list[UserPostReaction]:
        ...

    @classmethod
    async def filter_get_user_post_reaction_by_id(
        cls,
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def create_user_post_reaction(
        cls,
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def update_user_post_reaction(
        cls,
        session: AsyncSession,
    ) -> UserPostReaction:
        ...

    @classmethod
    async def delete_user_post_reaction(
        cls,
        session: AsyncSession,
    ) -> None:
        ...


class GroupPostService:

    # --- --- Posts --- ---

    @classmethod
    async def filter_get_group_posts(
        cls,
        session: AsyncSession,
    ) -> list[GroupPost]:
        ...

    @classmethod
    async def filter_get_group_post_by_id(
        cls,
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def create_group_post(
        cls,
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def update_group_post(
        cls,
        session: AsyncSession,
    ) -> GroupPost:
        ...

    @classmethod
    async def delete_group_post(
        cls,
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_group_post_comments(
        cls,
        session: AsyncSession,
    ) -> list[GroupPostComment]:
        ...

    @classmethod
    async def filter_get_group_post_comment_by_id(
        cls,
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def create_group_post_comment(
        cls,
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def update_group_post_comment(
        cls,
        session: AsyncSession,
    ) -> GroupPostComment:
        ...

    @classmethod
    async def delete_group_post_comment(
        cls,
        session: AsyncSession,
    ) -> None:
        ...

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_group_post_reactions(
        cls,
        session: AsyncSession,
    ) -> list[GroupPostReaction]:
        ...

    @classmethod
    async def filter_get_group_post_reaction_by_id(
        cls,
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def create_group_post_reaction(
        cls,
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def update_group_post_reaction(
        cls,
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def delete_group_post_reaction(
        cls,
        session: AsyncSession,
    ) -> None:
        ...
