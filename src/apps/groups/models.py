from uuid import UUID
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from src.core.models import TimeStampedUUIDModelBase
from src.apps.groups.enums import GroupMemberStatus, GroupRequestStatus, GroupStatus


from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.apps.users.models import User


class GroupRequest(TimeStampedUUIDModelBase, table=True):
    group_id: UUID = Field(foreign_key="group.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)

    status: GroupRequestStatus = Field(
        sa_column=Column(
            Enum(GroupRequestStatus), default=None, nullable=True, index=False
        )
    )

    group: Optional["Group"] = Relationship(
        sa_relationship=relationship("Group", back_populates="requests")
    )
    user: Optional["User"] = Relationship(
        sa_relationship=relationship("User", back_populates="membership_requests")
    )


class GroupRequestOutputSchema(SQLModel):
    group_id: UUID
    user_id: UUID
    status: GroupRequestStatus


class GroupMembership(TimeStampedUUIDModelBase, table=True):
    group_id: UUID = Field(foreign_key="group.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)

    membership_status: GroupMemberStatus = Field(
        sa_column=Column(
            Enum(GroupMemberStatus), default=None, nullable=True, index=False
        )
    )

    group: Optional["Group"] = Relationship(
        sa_relationship=relationship("Group", back_populates="members")
    )
    user: Optional["User"] = Relationship(
        sa_relationship=relationship("User", back_populates="memberships")
    )


class GroupMembershipOutputSchema(SQLModel):
    group_id: UUID
    user_id: UUID
    membership_status: GroupMemberStatus


class Group(TimeStampedUUIDModelBase, table=True):
    name: str = Field(sa_column=Column("name", String, unique=True))
    description: str
    status: GroupStatus = Field(sa_column=Column(Enum(GroupStatus)))

    requests: list[GroupRequest] = Relationship(
        sa_relationship=relationship(
            "GroupRequest",
            cascade="all, delete",
            back_populates="group",
        )
    )
    members: list[GroupMembership] = Relationship(
        sa_relationship=relationship(
            "GroupMembership",
            cascade="all, delete",
            back_populates="group",
        )
    )


class GroupOutputSchema(SQLModel):
    name: str
    description: str
    status: GroupStatus


class GroupInputSchema(SQLModel):
    name: str = Field(min_length=5)
    description: str
    status: GroupStatus
