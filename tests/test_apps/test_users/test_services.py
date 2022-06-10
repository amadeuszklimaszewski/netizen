from re import A
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
    PermissionDeniedException,
)


@pytest.mark.asyncio
async def test_friend_service_correctly_creates_friend_request(
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
):
    friend_request = await FriendService.create_friend_request(
        user_id=other_user_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.receiver_user == other_user_in_db
    assert friend_request.sender_user == user_in_db

    requests = (await session.exec(select(FriendRequest))).all()
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_create_friend_request_raises_exception_with_pending_request(
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
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
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
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
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
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
    user_in_db: User,
    other_user_in_db: User,
    session: AsyncSession,
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


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_friend_list(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    session: AsyncSession,
):
    friends = await FriendService.filter_friend_list(
        request_user=user_in_db,
        session=session,
    )
    assert friends[0] == friends_in_db[0]
    assert friends[0].friend_user_id == other_user_in_db.id


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_friend_by_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    session: AsyncSession,
):
    friend = await FriendService.filter_friend_by_id(
        friend_id=friends_in_db[0].id,
        request_user=user_in_db,
        session=session,
    )
    assert friend.id == friends_in_db[0].id
    assert friend.user_id == friends_in_db[0].user_id
    assert friend.friend_user_id == friends_in_db[0].friend_user_id


@pytest.mark.asyncio
async def test_filter_friend_by_id_raises_exception_with_invalid_friend_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        friend = await FriendService.filter_friend_by_id(
            friend_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_received_friend_request_list(
    user_in_db: User,
    other_user_in_db: User,
    received_friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    friends = await FriendService.filter_received_friend_requests(
        request_user=user_in_db,
        session=session,
    )
    assert friends[0].to_user_id == user_in_db.id
    assert friends[0].from_user_id == other_user_in_db.id


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_sent_friend_request_list(
    user_in_db: User,
    other_user_in_db: User,
    friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    friends = await FriendService.filter_sent_friend_requests(
        request_user=user_in_db,
        session=session,
    )
    assert friends[0].to_user_id == other_user_in_db.id
    assert friends[0].from_user_id == user_in_db.id


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_received_friend_request_by_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    received_friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    friend_request = await FriendService.filter_received_friend_request_by_id(
        friend_request_id=received_friend_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.id == received_friend_request_in_db.id
    assert friend_request.to_user_id == received_friend_request_in_db.to_user_id
    assert friend_request.from_user_id == received_friend_request_in_db.from_user_id
    assert friend_request.status == received_friend_request_in_db.status


@pytest.mark.asyncio
async def test_filter_received_friend_request_by_id_raises_does_not_exist_with_sent_request(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        friend_request = await FriendService.filter_received_friend_request_by_id(
            friend_request_id=friend_request_in_db.id,
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_filter_received_friend_request_by_id_raises_does_not_exist_with_wrong_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        friend_request = await FriendService.filter_received_friend_request_by_id(
            friend_request_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_friend_service_correctly_filters_sent_friend_request_by_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    friend_request = await FriendService.filter_sent_friend_request_by_id(
        friend_request_id=friend_request_in_db.id,
        request_user=user_in_db,
        session=session,
    )
    assert friend_request.id == friend_request_in_db.id
    assert friend_request.to_user_id == friend_request_in_db.to_user_id
    assert friend_request.from_user_id == friend_request_in_db.from_user_id
    assert friend_request.status == friend_request_in_db.status


@pytest.mark.asyncio
async def test_filter_sent_friend_request_by_id_raises_does_not_exist_with_received_request(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    received_friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        friend_request = await FriendService.filter_sent_friend_request_by_id(
            friend_request_id=received_friend_request_in_db.id,
            request_user=user_in_db,
            session=session,
        )


@pytest.mark.asyncio
async def test_filter_sent_friend_request_by_id_raises_does_not_exist_with_wrong_id(
    user_in_db: User,
    other_user_in_db: User,
    friends_in_db: tuple[Friend],
    friend_request_in_db: FriendRequest,
    session: AsyncSession,
):
    with pytest.raises(DoesNotExistException):
        friend_request = await FriendService.filter_sent_friend_request_by_id(
            friend_request_id=uuid4(),
            request_user=user_in_db,
            session=session,
        )
