from enum import Enum


class GroupStatus(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    CLOSED = "CLOSED"


class GroupMemberStatus(str, Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    REGULAR = "REGULAR"


class GroupRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
