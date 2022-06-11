import datetime as dt
from uuid import UUID
from dateutil.relativedelta import relativedelta
from typing import Any, TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field, Column, String, Enum
from sqlalchemy.orm import relationship
from src.apps.posts.enums import ReactionEnum
from src.core.models import TimeStampedUUIDModelBase

if TYPE_CHECKING:
    from src.apps.users.models import User
    from src.apps.groups.models import Group

# --- --- Posts --- ---


class UserPost(TimeStampedUUIDModelBase, table=True):
    text: str

    user_id: UUID = Field(foreign_key="user.id")


class PostOutputSchema(TimeStampedUUIDModelBase):
    text: str
    user_id: UUID


class GroupPost(TimeStampedUUIDModelBase, table=True):
    text: str

    group_id: UUID = Field(foreign_key="group.id")
    user_id: UUID = Field(foreign_key="user.id")


class GroupPostOutputSchema(PostOutputSchema):
    group_id: UUID


class PostInputSchema(SQLModel):
    text: str


# --- --- Comments --- ---


class UserPostComment(TimeStampedUUIDModelBase, table=True):
    text: str

    post_id: UUID = Field(foreign_key="userpost.id")
    user_id: UUID = Field(foreign_key="user.id")


class GroupPostComment(TimeStampedUUIDModelBase, table=True):
    text: str

    post_id: UUID = Field(foreign_key="grouppost.id")
    user_id: UUID = Field(foreign_key="user.id")


class CommentInputSchema(SQLModel):
    text: str


class CommentOutputSchema(TimeStampedUUIDModelBase):
    text: str
    post_id: UUID
    user_id: UUID


# --- --- Reactions --- ---


class UserPostReaction(TimeStampedUUIDModelBase, table=True):
    post_id: UUID = Field(foreign_key="userpost.id")
    user_id: UUID = Field(foreign_key="user.id")
    reaction: ReactionEnum = Field(sa_column=Column(Enum(ReactionEnum), index=False))

    # group: Optional["Group"] = Relationship(sa_relationship=relationship("Group"))
    # user: Optional["User"] = Relationship(sa_relationship=relationship("User"))


class GroupPostReaction(TimeStampedUUIDModelBase, table=True):
    post_id: UUID = Field(foreign_key="grouppost.id")
    user_id: UUID = Field(foreign_key="user.id")
    reaction: ReactionEnum = Field(sa_column=Column(Enum(ReactionEnum), index=False))


class PostReactionOutputSchema(TimeStampedUUIDModelBase):
    text: str
    reaction: ReactionEnum
    post_id: UUID
    user_id: UUID
