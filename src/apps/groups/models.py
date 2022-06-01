from uuid import UUID
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship, Column, String
from sqlalchemy.types import Enum
from src.core.models import TimeStampedUUIDModelBase
from src.apps.groups.enums import GroupMemberStatus, GroupRequestStatus, GroupStatus


from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.apps.users.models import User


class GroupRequest(TimeStampedUUIDModelBase, table=True):
    group_id: UUID = Field(default=None, foreign_key="group.id", primary_key=True)
    user_id: UUID = Field(default=None, foreign_key="user.id", primary_key=True)

    status: GroupRequestStatus = Field(
        sa_column=Column(
            Enum(GroupRequestStatus), default=None, nullable=True, index=False
        )
    )

    group: Optional["Group"] = Relationship(back_populates="requests")
    user: Optional["User"] = Relationship(back_populates="membership_requests")


class GroupRequestOutputSchema(GroupRequest):
    ...


class GroupMembership(TimeStampedUUIDModelBase, table=True):
    group_id: UUID = Field(default=None, foreign_key="group.id", primary_key=True)
    user_id: UUID = Field(default=None, foreign_key="user.id", primary_key=True)

    membership_status: GroupMemberStatus = Field(
        sa_column=Column(
            Enum(GroupRequestStatus), default=None, nullable=True, index=False
        )
    )

    group: Optional["Group"] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(back_populates="memberships")


class GroupMembershipOutputSchema(GroupMembership):
    ...


class GroupBase(SQLModel):
    name: str = Field(sa_column=Column("name", String, unique=True))
    description: str
    status: GroupStatus = Field(sa_column=Column(Enum(GroupStatus)))


class Group(TimeStampedUUIDModelBase, GroupBase, table=True):
    requests: list[GroupRequest] = Relationship(back_populates="group")
    members: list[GroupMembership] = Relationship(back_populates="group")


class GroupOutputSchema(TimeStampedUUIDModelBase, GroupBase):
    ...


class GroupInputSchema(GroupBase):
    name: str = Field(min_length=5)
