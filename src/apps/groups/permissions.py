from src.core.exceptions import PermissionDeniedException
from src.apps.groups.models import GroupMembership


async def validate_user_is_moderator_or_admin(membership: GroupMembership):
    if membership is None or membership.membership_status == "REGULAR":
        raise PermissionDeniedException("User unauthorized.")


async def validate_user_is_admin(membership: GroupMembership):
    if not membership or membership.membership_status != "ADMIN":
        raise PermissionDeniedException("User unathorized.")
