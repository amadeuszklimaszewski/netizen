from uuid import UUID
from pydantic import BaseModel
from src.core.models import TimeStampedUUIDModelBase
from src.apps.posts.enums import ReactionEnum


class PostInputSchema(BaseModel):
    text: str


class PostOutputSchema(TimeStampedUUIDModelBase):
    text: str
    user_id: UUID


class GroupPostOutputSchema(PostOutputSchema):
    group_id: UUID


class CommentInputSchema(BaseModel):
    text: str


class CommentOutputSchema(TimeStampedUUIDModelBase):
    text: str
    post_id: UUID
    user_id: UUID


class ReactionInputSchema(BaseModel):
    reaction: ReactionEnum


class ReactionOutputSchema(TimeStampedUUIDModelBase):
    reaction: ReactionEnum
    post_id: UUID
    user_id: UUID
