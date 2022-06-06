import pytest

from src.apps.groups.models import (
    GroupMembership,
)
from src.apps.groups.permissions import (
    validate_user_is_admin,
    validate_user_is_moderator_or_admin,
)
from src.core.exceptions import PermissionDeniedException


@pytest.mark.asyncio
async def test_validate_user_is_admin_raises_permission_denied_exception(
    group_membership_in_db: GroupMembership,
):
    with pytest.raises(PermissionDeniedException):
        await validate_user_is_admin(membership=group_membership_in_db)
    group_membership_in_db.membership_status = "MODERATOR"
    with pytest.raises(PermissionDeniedException):
        await validate_user_is_admin(membership=group_membership_in_db)


@pytest.mark.asyncio
async def test_validate_user_is_moderator_or_admin_raises_permission_denied_exception(
    group_membership_in_db: GroupMembership,
):
    with pytest.raises(PermissionDeniedException):
        await validate_user_is_moderator_or_admin(membership=group_membership_in_db)
