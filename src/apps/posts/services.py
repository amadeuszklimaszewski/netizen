from typing import Union
from uuid import UUID
from sqlmodel import select, update, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.groups.models import Group, GroupMembership
from src.apps.posts.models import (
    CommentInputSchema,
    GroupPost,
    GroupPostComment,
    GroupPostReaction,
    PostInputSchema,
    ReactionInputSchema,
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
        user = await get_object_by_id(Table=User, id=user_id, session=session)
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
        schema: PostInputSchema,
        user_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPost:
        user_post = await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        if request_user.id != user_post.user_id:
            raise PermissionDeniedException("User unauthorized.")
        update_data = schema.dict()
        await session.exec(
            update(UserPost).where(UserPost.id == post_id).values(**update_data)
        )
        await session.refresh(user_post)
        return user_post

    @classmethod
    async def delete_user_post(
        cls,
        user_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        user_post = await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        if request_user.id != user_post.user_id:
            raise PermissionDeniedException("User unauthorized.")
        await session.delete(user_post)
        await session.commit()
        return

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_user_post_comment_list(
        cls,
        user_id: UUID,
        post_id: UUID,
        session: AsyncSession,
    ) -> list[UserPostComment]:
        await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        return (
            await session.exec(
                select(UserPostComment).where(UserPostComment.post_id == post_id)
            )
        ).all()

    @classmethod
    async def filter_get_user_post_comment_by_id(
        cls,
        user_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        session: AsyncSession,
    ) -> UserPostComment:
        await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        user_post_comment = (
            await session.exec(
                select(UserPostComment).where(UserPostComment.id == comment_id)
            )
        ).first()
        if user_post_comment is None:
            raise DoesNotExistException("Comment with given id does not exist")
        return user_post_comment

    @classmethod
    async def create_user_post_comment(
        cls,
        schema: CommentInputSchema,
        user_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPostComment:
        user_post = await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )

        user_post_comment_data = schema.dict()
        user_post_comment = UserPostComment(
            **user_post_comment_data, user_id=request_user.id, post_id=post_id
        )
        session.add(user_post_comment)
        await session.commit()
        await session.refresh(user_post_comment)
        return user_post_comment

    @classmethod
    async def update_user_post_comment(
        cls,
        schema: CommentInputSchema,
        user_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPostComment:
        user_post_comment = await cls.filter_get_user_post_comment_by_id(
            user_id=user_id, post_id=post_id, comment_id=comment_id, session=session
        )
        if request_user.id != user_post_comment.user_id:
            raise PermissionDeniedException("User unauthorized.")

        user_post_comment_update_data = schema.dict()
        await session.exec(
            update(UserPostComment)
            .where(UserPostComment.id == comment_id)
            .values(**user_post_comment_update_data)
        )
        await session.refresh(user_post_comment)
        return user_post_comment

    @classmethod
    async def delete_user_post_comment(
        cls,
        user_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        user_post_comment = await cls.filter_get_user_post_comment_by_id(
            user_id=user_id, post_id=post_id, comment_id=comment_id, session=session
        )
        if request_user.id != user_post_comment.user_id:
            raise PermissionDeniedException("User unauthorized.")
        await session.delete(user_post_comment)
        await session.commit()
        return

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_user_post_reaction_list(
        cls,
        user_id: UUID,
        post_id: UUID,
        session: AsyncSession,
    ) -> list[UserPostReaction]:
        await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        return (
            await session.exec(
                select(UserPostReaction).where(UserPostReaction.post_id == post_id)
            )
        ).all()

    @classmethod
    async def filter_get_user_post_reaction_by_id(
        cls,
        user_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        session: AsyncSession,
    ) -> UserPostReaction:
        await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )
        user_post_reaction = (
            await session.exec(
                select(UserPostReaction).where(UserPostReaction.id == reaction_id)
            )
        ).first()
        if user_post_reaction is None:
            raise DoesNotExistException("Comment with given id does not exist")
        return user_post_reaction

    @classmethod
    async def create_user_post_reaction(
        cls,
        schema: ReactionInputSchema,
        user_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPostReaction:
        user_post = await cls.filter_get_user_post_by_id(
            user_id=user_id, post_id=post_id, session=session
        )

        user_post_reaction_data = schema.dict()
        user_post_reaction = UserPostReaction(
            **user_post_reaction_data, user_id=request_user.id, post_id=post_id
        )
        session.add(user_post_reaction)
        await session.commit()
        await session.refresh(user_post_reaction)
        return user_post_reaction

    @classmethod
    async def update_user_post_reaction(
        cls,
        schema: ReactionInputSchema,
        user_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> UserPostReaction:
        user_post_reaction = await cls.filter_get_user_post_reaction_by_id(
            user_id=user_id, post_id=post_id, reaction_id=reaction_id, session=session
        )
        if request_user.id != user_post_reaction.user_id:
            raise PermissionDeniedException("User unauthorized.")

        user_post_comment_update_data = schema.dict()
        await session.exec(
            update(UserPostReaction)
            .where(UserPostReaction.id == reaction_id)
            .values(**user_post_comment_update_data)
        )
        await session.refresh(user_post_reaction)
        return user_post_reaction

    @classmethod
    async def delete_user_post_reaction(
        cls,
        user_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        user_post_reaction = await cls.filter_get_user_post_reaction_by_id(
            user_id=user_id, post_id=post_id, reaction_id=reaction_id, session=session
        )
        if request_user.id != user_post_reaction.user_id:
            raise PermissionDeniedException("User unauthorized.")
        await session.delete(user_post_reaction)
        await session.commit()
        return


class GroupPostService:

    # --- --- Utils --- ---

    @classmethod
    async def _validate_user_access_on_get(
        cls,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> bool:
        group = await get_object_by_id(Table=Group, id=group_id, session=session)

        membership = None
        if request_user:
            membership = (
                await session.exec(
                    select(GroupMembership).where(
                        and_(
                            GroupMembership.group_id == group_id,
                            GroupMembership.user_id == request_user.id,
                        )
                    )
                )
            ).first()
        if not membership and group.status != "PUBLIC":
            raise PermissionDeniedException("User unauthorized.")
        return True

    @classmethod
    async def _validate_user_access_on_post_put_delete(
        cls,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> bool:
        group = await get_object_by_id(Table=Group, id=group_id, session=session)

        membership = None
        if request_user:
            membership = (
                await session.exec(
                    select(GroupMembership).where(
                        and_(
                            GroupMembership.group_id == group_id,
                            GroupMembership.user_id == request_user.id,
                        )
                    )
                )
            ).first()
        if not membership:
            raise PermissionDeniedException("User unauthorized.")
        return True

    @classmethod
    async def _find_group_post(
        cls,
        group_id: UUID,
        post_id: UUID,
        session: AsyncSession,
    ) -> GroupPost:
        group_post = (
            await session.exec(
                select(GroupPost).where(
                    and_(
                        GroupPost.group_id == group_id,
                        GroupPost.id == post_id,
                    )
                )
            )
        ).first()
        if group_post is None:
            raise DoesNotExistException("Group post with given id does not exist.")
        return group_post

    @classmethod
    async def _find_group_post_comment(
        cls,
        group_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        session: AsyncSession,
    ) -> GroupPostComment:

        group_post_comment = (
            await session.exec(
                select(GroupPostComment)
                .join(GroupPostComment.post)
                .where(
                    and_(
                        GroupPost.group_id == group_id,
                        GroupPostComment.post_id == post_id,
                        GroupPostComment.id == comment_id,
                    )
                )
            )
        ).first()
        if group_post_comment is None:
            raise DoesNotExistException(
                "Group post comment with given id does not exist"
            )
        return group_post_comment

    @classmethod
    async def _find_group_post_reaction(
        cls,
        group_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        session: AsyncSession,
    ) -> GroupPostReaction:

        group_post_reaction = (
            await session.exec(
                select(GroupPostReaction)
                .join(GroupPostReaction.post)
                .where(
                    and_(
                        GroupPost.group_id == group_id,
                        GroupPostReaction.post_id == post_id,
                        GroupPostReaction.id == reaction_id,
                    )
                )
            )
        ).first()
        if group_post_reaction is None:
            raise DoesNotExistException(
                "Group post reaction with given id does not exist"
            )
        return group_post_reaction

    # --- --- Posts --- ---

    @classmethod
    async def filter_get_group_post_list(
        cls,
        group_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> list[GroupPost]:
        await cls._validate_user_access_on_get(
            group_id=group_id, request_user=request_user, session=session
        )

        return (
            await session.exec(select(GroupPost).where(GroupPost.group_id == group_id))
        ).all()

    @classmethod
    async def filter_get_group_post_by_id(
        cls,
        group_id: UUID,
        post_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> GroupPost:
        await cls._validate_user_access_on_get(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post = await cls._find_group_post(
            group_id=group_id,
            post_id=post_id,
            session=session,
        )
        return group_post

    @classmethod
    async def create_group_post(
        cls,
        schema: PostInputSchema,
        group_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPost:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post_data = schema.dict()
        group_post = GroupPost(
            **group_post_data, user_id=request_user.id, group_id=group_id
        )
        session.add(group_post)
        await session.commit()
        await session.refresh(group_post)
        return group_post

    @classmethod
    async def update_group_post(
        cls,
        schema: PostInputSchema,
        group_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPost:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post = await cls._find_group_post(
            group_id=group_id,
            post_id=post_id,
            session=session,
        )
        if request_user.id != group_post.user_id:
            raise PermissionDeniedException("User unauthorized.")

        group_post_update_data = schema.dict()
        await session.exec(
            update(GroupPost)
            .where(GroupPost.id == post_id)
            .values(**group_post_update_data)
        )
        await session.refresh(group_post)
        return group_post

    @classmethod
    async def delete_group_post(
        cls,
        group_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post = await cls._find_group_post(
            group_id=group_id,
            post_id=post_id,
            session=session,
        )
        if request_user.id != group_post.user_id:
            raise PermissionDeniedException("User unauthorized.")

        await session.delete(group_post)
        await session.commit()
        return

    # --- --- Comments --- ---

    @classmethod
    async def filter_get_group_post_comment_list(
        cls,
        group_id: UUID,
        post_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> list[GroupPostComment]:
        group_post = await cls.filter_get_group_post_by_id(
            group_id=group_id,
            post_id=post_id,
            request_user=request_user,
            session=session,
        )
        return (
            await session.exec(
                select(GroupPostComment).where(GroupPostComment.post_id == post_id)
            )
        ).all()

    @classmethod
    async def filter_get_group_post_comment_by_id(
        cls,
        group_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> GroupPostComment:
        group_post = await cls.filter_get_group_post_by_id(
            group_id=group_id,
            post_id=post_id,
            request_user=request_user,
            session=session,
        )
        group_post_comment = group_post_comment = await cls._find_group_post_comment(
            group_id=group_id, post_id=post_id, comment_id=comment_id, session=session
        )
        return group_post_comment

    @classmethod
    async def create_group_post_comment(
        cls,
        schema: CommentInputSchema,
        group_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPostComment:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        post = await cls._find_group_post(
            group_id=group_id, post_id=post_id, session=session
        )
        group_post_comment_data = schema.dict()
        group_post_comment = GroupPostComment(
            **group_post_comment_data, user_id=request_user.id, post_id=post_id
        )
        session.add(group_post_comment)
        await session.commit()
        await session.refresh(group_post_comment)
        return group_post_comment

    @classmethod
    async def update_group_post_comment(
        cls,
        schema: CommentInputSchema,
        group_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPostComment:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post_comment = await cls._find_group_post_comment(
            group_id=group_id, post_id=post_id, comment_id=comment_id, session=session
        )
        if request_user.id != group_post_comment.user_id:
            raise PermissionDeniedException("User unauthorized.")

        group_post_comment_update_data = schema.dict()
        await session.exec(
            update(GroupPostComment)
            .where(GroupPostComment.id == comment_id)
            .values(**group_post_comment_update_data)
        )
        await session.refresh(group_post_comment)
        return group_post_comment

    @classmethod
    async def delete_group_post_comment(
        cls,
        group_id: UUID,
        post_id: UUID,
        comment_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        await cls._validate_user_access_on_post_put_delete(
            group_id=group_id, request_user=request_user, session=session
        )
        group_post_comment = await cls._find_group_post_comment(
            group_id=group_id, post_id=post_id, comment_id=comment_id, session=session
        )
        if request_user.id != group_post_comment.user_id:
            raise PermissionDeniedException("User unauthorized.")

        await session.delete(group_post_comment)
        await session.commit()
        return

    # --- --- Reactions --- ---

    @classmethod
    async def filter_get_group_post_reaction_list(
        cls,
        group_id: UUID,
        post_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> list[GroupPostReaction]:
        group_post = await cls.filter_get_group_post_by_id(
            group_id=group_id,
            post_id=post_id,
            request_user=request_user,
            session=session,
        )
        return (
            await session.exec(
                select(GroupPostReaction).where(GroupPostReaction.post_id == post_id)
            )
        ).all()

    @classmethod
    async def filter_get_group_post_reaction_by_id(
        cls,
        group_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        request_user: Union[User, None],
        session: AsyncSession,
    ) -> GroupPostReaction:
        group_post = await cls.filter_get_group_post_by_id(
            group_id=group_id,
            post_id=post_id,
            request_user=request_user,
            session=session,
        )
        group_post_reaction = await cls._find_group_post_reaction(
            group_id=group_id, post_id=post_id, reaction_id=reaction_id, session=session
        )
        return group_post_reaction

    @classmethod
    async def create_group_post_reaction(
        cls,
        schema: ReactionInputSchema,
        group_id: UUID,
        post_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def update_group_post_reaction(
        cls,
        schema: ReactionInputSchema,
        group_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> GroupPostReaction:
        ...

    @classmethod
    async def delete_group_post_reaction(
        cls,
        group_id: UUID,
        post_id: UUID,
        reaction_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> None:
        ...
