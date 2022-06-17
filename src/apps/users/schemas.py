from uuid import UUID
from typing import Any
import datetime as dt
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, validator, validate_email as validate_email_pd, Field
from src.apps.users.models import UserBase

from src.core.models import TimeStampedUUIDModelBase
from src.apps.users.enums import FriendRequestStatus


class UserOutputSchema(UserBase):
    is_active: bool


class LoginSchema(BaseModel):
    email: str
    password: str


class RegisterSchema(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    birthday: dt.date
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


class FriendOutputSchema(TimeStampedUUIDModelBase):
    user_id: UUID
    friend_user_id: UUID


class FriendRequestOutputSchema(TimeStampedUUIDModelBase):
    from_user_id: UUID
    to_user_id: UUID
    status: FriendRequestStatus


class FriendRequestUpdateSchema(BaseModel):
    status: FriendRequestStatus
