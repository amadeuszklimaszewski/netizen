from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from src.apps.posts.services import UserPostService

from src.database.connection import get_db
from src.apps.users.models import User
from src.dependencies.users import authenticate_user
from src.apps.posts.schemas import (
    PostInputSchema,
    PostOutputSchema,
    CommentInputSchema,
    CommentOutputSchema,
    ReactionInputSchema,
    ReactionOutputSchema,
)


user_post_router = APIRouter()


@user_post_router.get(
    "/{user_id}/posts/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=list[PostOutputSchema],
)
async def get_user_post_list(
    user_id: UUID,
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[PostOutputSchema]:
    return [
        PostOutputSchema.from_orm(user_post)
        for user_post in (
            await post_service.filter_get_user_post_list(
                user_id=user_id, session=session
            )
        )
    ]


@user_post_router.post(
    "/{user_id}/posts/",
    tags=["user-posts"],
    status_code=status.HTTP_201_CREATED,
    response_model=PostOutputSchema,
)
async def create_user_post(
    schema: PostInputSchema,
    user_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PostOutputSchema:
    user_post = await post_service.create_user_post(
        schema=schema, user_id=user_id, request_user=request_user, session=session
    )
    return PostOutputSchema.from_orm(user_post)


@user_post_router.get(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=PostOutputSchema,
)
async def get_user_post_by_id(
    user_id: UUID,
    post_id: UUID,
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PostOutputSchema:
    user_post = await post_service.filter_get_user_post_by_id(
        user_id=user_id, post_id=post_id, session=session
    )
    return PostOutputSchema.from_orm(user_post)


@user_post_router.put(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_200_OK,
    response_model=PostOutputSchema,
)
async def update_user_post(
    schema: PostInputSchema,
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PostOutputSchema:
    user_post = await post_service.update_user_post(
        schema=schema,
        user_id=user_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return PostOutputSchema.from_orm(user_post)


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/",
    tags=["user-posts"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_post(
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_user_post(
        user_id=user_id, post_id=post_id, request_user=request_user, session=session
    )
    return


@user_post_router.get(
    "/{user_id}/posts/{post_id}/comments/",
    tags=["user-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=list[CommentOutputSchema],
)
async def get_user_post_comment_list(
    user_id: UUID,
    post_id: UUID,
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[CommentOutputSchema]:
    return [
        CommentOutputSchema.from_orm(user_post_comment)
        for user_post_comment in (
            await post_service.filter_get_user_post_comment_list(
                user_id=user_id, post_id=post_id, session=session
            )
        )
    ]


@user_post_router.post(
    "/{user_id}/posts/{post_id}/comments/",
    tags=["user-post-comments"],
    status_code=status.HTTP_201_CREATED,
    response_model=CommentOutputSchema,
)
async def create_user_post_comment(
    schema: CommentInputSchema,
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    user_post_comment = await post_service.create_user_post_comment(
        schema=schema,
        user_id=user_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return CommentOutputSchema.from_orm(user_post_comment)


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
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    user_post_comment = await post_service.filter_get_user_post_comment_by_id(
        user_id=user_id, post_id=post_id, comment_id=comment_id, session=session
    )
    return CommentOutputSchema.from_orm(user_post_comment)


@user_post_router.put(
    "/{user_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["user-post-comments"],
    status_code=status.HTTP_200_OK,
    response_model=CommentOutputSchema,
)
async def update_user_post_comment(
    schema: CommentInputSchema,
    user_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> CommentOutputSchema:
    user_post_comment = await post_service.update_user_post_comment(
        schema=schema,
        user_id=user_id,
        post_id=post_id,
        comment_id=comment_id,
        request_user=request_user,
        session=session,
    )
    return CommentOutputSchema.from_orm(user_post_comment)


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/comments/{comment_id}/",
    tags=["user-post-comments"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_post_comment(
    user_id: UUID,
    post_id: UUID,
    comment_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_user_post_comment(
        user_id=user_id,
        post_id=post_id,
        comment_id=comment_id,
        request_user=request_user,
        session=session,
    )
    return


@user_post_router.get(
    "/{user_id}/posts/{post_id}/reactions/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=list[ReactionOutputSchema],
)
async def get_user_post_reaction_list(
    user_id: UUID,
    post_id: UUID,
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> list[ReactionOutputSchema]:
    return [
        ReactionOutputSchema.from_orm(user_post_reaction)
        for user_post_reaction in (
            await post_service.filter_get_user_post_reaction_list(
                user_id=user_id, post_id=post_id, session=session
            )
        )
    ]


@user_post_router.post(
    "/{user_id}/posts/{post_id}/reactions/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionOutputSchema,
)
async def create_user_post_reaction(
    schema: ReactionInputSchema,
    user_id: UUID,
    post_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    user_post_comment = await post_service.create_user_post_reaction(
        schema=schema,
        user_id=user_id,
        post_id=post_id,
        request_user=request_user,
        session=session,
    )
    return ReactionOutputSchema.from_orm(user_post_comment)


@user_post_router.get(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=ReactionOutputSchema,
)
async def get_user_post_reaction_by_id(
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    user_post_reaction = await post_service.filter_get_user_post_reaction_by_id(
        user_id=user_id, post_id=post_id, reaction_id=reaction_id, session=session
    )
    return ReactionOutputSchema.from_orm(user_post_reaction)


@user_post_router.put(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_200_OK,
    response_model=ReactionOutputSchema,
)
async def update_user_post_reaction(
    schema: ReactionInputSchema,
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> ReactionOutputSchema:
    user_post_reaction = await post_service.update_user_post_reaction(
        schema=schema,
        user_id=user_id,
        post_id=post_id,
        reaction_id=reaction_id,
        request_user=request_user,
        session=session,
    )
    return ReactionOutputSchema.from_orm(user_post_reaction)


@user_post_router.delete(
    "/{user_id}/posts/{post_id}/reactions/{reaction_id}/",
    tags=["user-post-reactions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_post_reaction(
    user_id: UUID,
    post_id: UUID,
    reaction_id: UUID,
    request_user: User = Depends(authenticate_user),
    post_service: UserPostService = Depends(),
    session: AsyncSession = Depends(get_db),
) -> None:
    await post_service.delete_user_post_reaction(
        user_id=user_id,
        post_id=post_id,
        reaction_id=reaction_id,
        request_user=request_user,
        session=session,
    )
    return
