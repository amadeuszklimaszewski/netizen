from uuid import UUID
from typing import Union

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.connection import get_db
from src.apps.users.models import User
from src.dependencies.users import authenticate_user, get_user_or_none
from src.apps.posts.models import (
    PostInputSchema,
    PostOutputSchema,
    CommentInputSchema,
    CommentOutputSchema,
    PostReactionOutputSchema,
)


user_post_router = APIRouter()


@user_post_router.get(
    "/{user_id}/posts/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=list[PostOutputSchema],
)
async def get_user_posts(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.post(
    "/{user_id}/posts/",
    tags=["user-posts"],
    status_code=status.HTTP_201_CREATED,
    response_model=PostOutputSchema,
)
async def create_user_post(
    user_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.get(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=PostOutputSchema,
)
async def get_user_post_by_id(
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.put(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=PostOutputSchema,
)
async def update_user_post(
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_post(
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.get(
    "/{user_id}/posts/{post_id}/comments/",
    tags=["user-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=list[CommentOutputSchema],
)
async def get_user_post_comment_list(
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.post(
    "/{user_id}/posts/{post_id}/comments/",
    tags=["user-post-comments"],
    status_code=status.HTTP_201_CREATED,
    response_model=CommentOutputSchema,
)
async def create_user_post_comment(
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.get(
    "/{user_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["user-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=CommentOutputSchema,
)
async def get_user_post_comment_by_id(
    user_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.put(
    "/{user_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["user-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=CommentOutputSchema,
)
async def update_user_post_comment(
    user_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["user-post-comments"],
    status_code=status.HTTP_201_CREATED,
)
async def delete_user_post_comment(
    user_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.get(
    "/{user_id}/posts/{post_id}/reactions/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=list[CommentOutputSchema],
)
async def get_user_post_reaction_list(
    user_id: UUID,
    post_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.post(
    "/{user_id}/posts/{post_id}/reactions/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_201_CREATED,
    response_model=PostReactionOutputSchema,
)
async def create_user_post_reaction(
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.get(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=PostReactionOutputSchema,
)
async def get_user_post_reaction_by_id(
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.put(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=PostReactionOutputSchema,
)
async def update_user_post_reaction(
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_201_CREATED,
)
async def delete_user_post_reaction(
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
):
    ...
