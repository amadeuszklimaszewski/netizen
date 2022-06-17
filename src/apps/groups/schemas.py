from uuid import UUID
from pydantic import BaseModel
from sqlmodel import Field
from src.core.models import TimeStampedUUIDModelBase
from src.apps.groups.enums import GroupMemberStatus, GroupRequestStatus, GroupStatus


class GroupInputSchema(BaseModel):
    name: str = Field(..., min_length=5)
    description: str
    status: GroupStatus


class GroupOutputSchema(TimeStampedUUIDModelBase):
    name: str
    description: str
    status: GroupStatus


class GroupMembershipUpdateSchema(BaseModel):
    membership_status: GroupMemberStatus


class GroupMembershipOutputSchema(TimeStampedUUIDModelBase):
    group_id: UUID
    user_id: UUID
    membership_status: GroupMemberStatus


class GroupRequestUpdateSchema(BaseModel):
    status: GroupRequestStatus


class GroupRequestOutputSchema(TimeStampedUUIDModelBase):
    group_id: UUID
    user_id: UUID
    status: GroupRequestStatus
