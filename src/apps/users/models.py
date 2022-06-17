import datetime as dt
from uuid import UUID
from dateutil.relativedelta import relativedelta
from typing import Any, TYPE_CHECKING, Optional
from pydantic import BaseModel, validator, validate_email as validate_email_pd
from sqlmodel import Relationship, SQLModel, Field, Column, String, Enum
from sqlalchemy.orm import relationship
from src.apps.users.enums import FriendRequestStatus
from src.core.models import TimeStampedUUIDModelBase

if TYPE_CHECKING:
    from src.apps.groups.models import GroupRequest, GroupMembership


class UserBase(TimeStampedUUIDModelBase):
    username: str = Field(sa_column=Column("username", String, unique=True))
    email: str = Field(sa_column=Column("email", String, unique=True))
    first_name: str
    last_name: str
    birthday: dt.date


class User(UserBase, table=True):
    hashed_password: str
    is_active: bool = False

    membership_requests: list["GroupRequest"] = Relationship(
        sa_relationship=relationship(
            "GroupRequest",
            cascade="all, delete",
            back_populates="user",
        )
    )
    memberships: list["GroupMembership"] = Relationship(
        sa_relationship=relationship(
            "GroupMembership",
            cascade="all, delete",
            back_populates="user",
        )
    )

    received_friend_requests: list["FriendRequest"] = Relationship(
        sa_relationship=relationship(
            "FriendRequest",
            cascade="all, delete",
            back_populates="receiver_user",
            primaryjoin="User.id == FriendRequest.to_user_id",
        )
    )
    sent_friend_requests: list["FriendRequest"] = Relationship(
        sa_relationship=relationship(
            "FriendRequest",
            cascade="all, delete",
            back_populates="sender_user",
            primaryjoin="User.id == FriendRequest.from_user_id",
        )
    )

    friends: list["Friend"] = Relationship(
        sa_relationship=relationship(
            "Friend",
            cascade="all, delete",
            back_populates="user",
            primaryjoin="User.id == Friend.user_id",
        )
    )


class Friend(TimeStampedUUIDModelBase, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    friend_user_id: UUID = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="friends",
            primaryjoin="Friend.user_id == User.id",
        )
    )


class FriendRequest(TimeStampedUUIDModelBase, table=True):
    from_user_id: UUID = Field(foreign_key="user.id")
    to_user_id: UUID = Field(foreign_key="user.id")
    status: FriendRequestStatus = Field(
        sa_column=Column(
            Enum(FriendRequestStatus), default=None, nullable=True, index=False
        )
    )

    sender_user: Optional["User"] = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="sent_friend_requests",
            primaryjoin="FriendRequest.from_user_id == User.id",
        )
    )
    receiver_user: Optional["User"] = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="received_friend_requests",
            primaryjoin="FriendRequest.to_user_id == User.id",
        )
    )
