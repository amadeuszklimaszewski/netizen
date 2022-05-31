from sqlmodel import Field, SQLModel, Relationship
from src.core.models import TimeStampedUUIDModelBase


class Group(TimeStampedUUIDModelBase, table=True):
    name: str
    description: str
    status: str
