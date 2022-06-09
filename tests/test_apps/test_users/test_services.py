from uuid import uuid4
import pytest
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.users.models import User, Friend, FriendRequest, FriendRequestUpdateSchema
from src.apps.users.services import FriendService
from src.apps.users.models import User
from src.core.exceptions import (
    AlreadyExistsException,
    DoesNotExistException,
    GroupRequestAlreadyHandled,
    PermissionDeniedException,
)


@pytest.mark.asyncio
async def test_friend_service_correctly_creates_friend_request(
    user_in_db: User, other_user_in_db: User, session: AsyncSession
):
    friend_request = await FriendService.create_friend_request(
        user_id=other_user_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.receiver_user == other_user_in_db
    assert friend_request.sender_user == user_in_db


@pytest.mark.asyncio
async def test_create_friend_request_raises_exception_with_pending_request(
    user_in_db: User, other_user_in_db: User, session: AsyncSession
):
    friend_request = FriendRequest(
        to_user_id=other_user_in_db.id, from_user_id=user_in_db.id, status="PENDING"
    )
    session.add(friend_request)
    await session.commit()
    with pytest.raises(AlreadyExistsException):
        friend_request = await FriendService.create_friend_request(
            user_id=other_user_in_db.id,
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_create_friend_request_does_not_raise_exception_with_denied_request(
    user_in_db: User, other_user_in_db: User, session: AsyncSession
):
    friend_request = FriendRequest(
        to_user_id=other_user_in_db.id, from_user_id=user_in_db.id, status="DENIED"
    )
    session.add(friend_request)
    await session.commit()

    friend_request = await FriendService.create_friend_request(
        user_id=other_user_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.receiver_user == other_user_in_db
    assert friend_request.sender_user == user_in_db


@pytest.mark.asyncio
async def test_create_friend_request_does_not_raise_exception_with_accepted_request(
    user_in_db: User, other_user_in_db: User, session: AsyncSession
):
    friend_request = FriendRequest(
        to_user_id=other_user_in_db.id, from_user_id=user_in_db.id, status="ACCEPTED"
    )
    session.add(friend_request)
    await session.commit()

    friend_request = await FriendService.create_friend_request(
        user_id=other_user_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.receiver_user == other_user_in_db
    assert friend_request.sender_user == user_in_db


@pytest.mark.asyncio
async def test_create_friend_request_raises_exception_with_existing_friend(
    user_in_db: User, other_user_in_db: User, session: AsyncSession
):
    friend = await FriendService.create_friend(
        user_id=user_in_db.id, friend_id=other_user_in_db.id, session=session
    )
    with pytest.raises(AlreadyExistsException):
        friend_request = await FriendService.create_friend_request(
            user_id=other_user_in_db.id,
            request_user=user_in_db,
            session=session,
        )
