from uuid import UUID
from typing import Union

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.posts.services import GroupPostService

from src.database.connection import get_db
from src.apps.users.models import User
from src.dependencies.users import authenticate_user, get_user_or_none
from src.apps.posts.schemas import (
    PostInputSchema,
    GroupPostOutputSchema,
    CommentInputSchema,
    CommentOutputSchema,
    ReactionInputSchema,
    ReactionOutputSchema,
)


group_post_router = APIRouter()


@group_post_router.get(
    "/{group_id}/posts/",
    tags=["group-posts"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupPostOutputSchema],
)
async def get_user_posts(
    group_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[GroupPostOutputSchema]:
    return [
        GroupPostOutputSchema.from_orm(user_post)
        for user_post in (
            await post_service.filter_get_group_post_list(
                group_id=group_id, request_user=request_user, session=session
            )
        )
    ]


@group_post_router.post(
    "/{group_id}/posts/",
    tags=["group-posts"],
    status_code=status.HTTP_201_CREATED,
    response_model=GroupPostOutputSchema,
)
async def create_user_post(
    schema: PostInputSchema,
    group_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> GroupPostOutputSchema:
    group_post = await post_service.create_group_post(
        schema=schema, group_id=group_id, request_user=request_user, session=session
    )
    return GroupPostOutputSchema.from_orm(group_post)


@group_post_router.get(
    "/{group_id}/posts/{post_id}/",
    tags=["group-posts"],
    status_code=status.HTTP_200_OK,
    response_model=GroupPostOutputSchema,
)
async def get_user_post_by_id(
    group_id: UUID,
    post_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> GroupPostOutputSchema:
    group_post = await post_service.filter_get_group_post_by_id(
        group_id=group_id, post_id=post_id, request_user=request_user, session=session
    )
    return GroupPostOutputSchema.from_orm(group_post)


@group_post_router.put(
    "/{group_id}/posts/{post_id}/",
    tags=["group-posts"],
    status_code=status.HTTP_200_OK,
    response_model=GroupPostOutputSchema,
)
async def update_user_post(
    schema: PostInputSchema,
    group_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> GroupPostOutputSchema:
    group_post = await post_service.update_group_post(
        schema=schema,
        group_id=group_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return GroupPostOutputSchema.from_orm(group_post)


@group_post_router.delete(
    "/{group_id}/posts/{post_id}/",
    tags=["group-posts"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_post(
    group_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_group_post(
        group_id=group_id, post_id=post_id, request_user=request_user, session=session
    )
    return


@group_post_router.get(
    "/{group_id}/posts/{post_id}/comments/",
    tags=["group-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=list[CommentOutputSchema],
)
async def get_group_post_comment_list(
    group_id: UUID,
    post_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[CommentOutputSchema]:
    return [
        CommentOutputSchema.from_orm(group_post_comment)
        for group_post_comment in (
            await post_service.filter_get_group_post_comment_list(
                group_id=group_id,
                post_id=post_id,
                request_user=request_user,
                session=session,
            )
        )
    ]


@group_post_router.post(
    "/{group_id}/posts/{post_id}/comments/",
    tags=["group-post-comments"],
    status_code=status.HTTP_201_CREATED,
    response_model=CommentOutputSchema,
)
async def create_group_post_comment(
    schema: CommentInputSchema,
    group_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    group_post_comment = await post_service.create_group_post_comment(
        schema=schema,
        group_id=group_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return CommentOutputSchema.from_orm(group_post_comment)


@group_post_router.get(
    "/{group_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["group-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=CommentOutputSchema,
)
async def get_group_post_comment_by_id(
    group_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    group_post_comment = await post_service.filter_get_group_post_comment_by_id(
        group_id=group_id,
        post_id=post_id,
        comment_id=comment_id,
        request_user=request_user,
        session=session,
    )
    return CommentOutputSchema.from_orm(group_post_comment)


@group_post_router.put(
    "/{group_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["group-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=CommentOutputSchema,
)
async def update_group_post_comment(
    schema: CommentInputSchema,
    group_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    group_post_comment = await post_service.update_group_post_comment(
        schema=schema,
        group_id=group_id,
        post_id=post_id,
        comment_id=comment_id,
        request_user=request_user,
        session=session,
    )
    return CommentOutputSchema.from_orm(group_post_comment)


@group_post_router.delete(
    "/{group_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["group-post-comments"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_post_comment(
    group_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_group_post_comment(
        group_id=group_id,
        post_id=post_id,
        comment_id=comment_id,
        request_user=request_user,
        session=session,
    )
    return


@group_post_router.get(
    "/{group_id}/posts/{post_id}/reactions/",
    tags=["group-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=list[ReactionOutputSchema],
)
async def get_group_post_reaction_list(
    group_id: UUID,
    post_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[ReactionOutputSchema]:
    return [
        ReactionOutputSchema.from_orm(group_post_reaction)
        for group_post_reaction in (
            await post_service.filter_get_group_post_reaction_list(
                group_id=group_id,
                post_id=post_id,
                request_user=request_user,
                session=session,
            )
        )
    ]


@group_post_router.post(
    "/{group_id}/posts/{post_id}/reactions/",
    tags=["group-post-reactions"],
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionOutputSchema,
)
async def create_group_post_reaction(
    schema: ReactionInputSchema,
    group_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    group_post_reaction = await post_service.create_group_post_reaction(
        schema=schema,
        group_id=group_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return ReactionOutputSchema.from_orm(group_post_reaction)


@group_post_router.get(
    "/{group_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["group-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=ReactionOutputSchema,
)
async def get_group_post_reaction_by_id(
    group_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: Union[User, None] = Depends(get_user_or_none),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    group_post_reaction = await post_service.filter_get_group_post_reaction_by_id(
        group_id=group_id,
        post_id=post_id,
        reaction_id=reaction_id,
        request_user=request_user,
        session=session,
    )
    return ReactionOutputSchema.from_orm(group_post_reaction)


@group_post_router.put(
    "/{group_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["group-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=ReactionOutputSchema,
)
async def update_group_post_reaction(
    schema: ReactionInputSchema,
    group_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    group_post_reaction = await post_service.update_group_post_reaction(
        schema=schema,
        group_id=group_id,
        post_id=post_id,
        reaction_id=reaction_id,
        request_user=request_user,
        session=session,
    )
    return ReactionOutputSchema.from_orm(group_post_reaction)


@group_post_router.delete(
    "/{group_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["group-post-reactions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_post_reaction(
    group_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: GroupPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_group_post_reaction(
        group_id=group_id,
        post_id=post_id,
        reaction_id=reaction_id,
        request_user=request_user,
        session=session,
    )
    return
