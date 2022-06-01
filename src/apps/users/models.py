import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import Any, TYPE_CHECKING
from pydantic import validator, validate_email as validate_email_pd
from sqlmodel import Relationship, SQLModel, Field, Column, String
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

    membership_requests: list["GroupRequest"] = Relationship(back_populates="user")
    memberships: list["GroupMembership"] = Relationship(back_populates="user")


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
