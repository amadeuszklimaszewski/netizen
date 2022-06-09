import datetime as dt
from uuid import UUID
from dateutil.relativedelta import relativedelta
from typing import Any, TYPE_CHECKING, Optional
from pydantic import validator, validate_email as validate_email_pd
from sqlmodel import Relationship, SQLModel, Field, Column, String
from sqlalchemy.orm import relationship
from src.apps.users.enums import FriendRequestStatus
from src.core.models import TimeStampedUUIDModelBase

if TYPE_CHECKING:
    from src.apps.groups.models import GroupRequest, GroupMembership


class UserBase(SQLModel):
    username: str = Field(sa_column=Column("username", String, unique=True))
    email: str = Field(sa_column=Column("email", String, unique=True))
    first_name: str
    last_name: str
    birthday: dt.date
    is_active: bool = True


class UserOutputSchema(TimeStampedUUIDModelBase, UserBase):
    ...


class User(TimeStampedUUIDModelBase, UserBase, table=True):
    hashed_password: str

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


class LoginSchema(SQLModel):
    email: str
    password: str


class RegisterSchema(UserBase):
    password: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)

    @validator("birthday")
    def validate_birthday(cls, birthday: dt.datetime) -> dt.datetime:
        if relativedelta(dt.date.today(), birthday).years <= 18:
            raise ValueError("You must be at least 18 years old")
        return birthday

    @validator("email")
    def validate_email(cls, email: str) -> str:
        validate_email_pd(email)
        return email

    @validator("password2")
    def validate_password(cls, password2: str, values: dict[str, Any]) -> str:
        if password2 != values["password"]:
            raise ValueError("Passwords do not match")
        return password2


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


class FriendOutputSchema(TimeStampedUUIDModelBase):
    user_id: UUID
    friend_user_id: UUID


class FriendRequest(TimeStampedUUIDModelBase, table=True):
    from_user_id: UUID = Field(foreign_key="user.id")
    to_user_id: UUID = Field(foreign_key="user.id")
    status: FriendRequestStatus

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


class FriendRequestOutputSchema(TimeStampedUUIDModelBase):
    from_user_id: UUID
    to_user_id: UUID
    status: FriendRequestStatus


class FriendRequestUpdateSchema(SQLModel):
    status: FriendRequestStatus
