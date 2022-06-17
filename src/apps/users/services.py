from typing import Union
from uuid import UUID
from sqlmodel import select, and_, or_, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.emails.services import EmailService
from src.apps.users.models import (
    Friend,
    FriendRequest,
    FriendRequestUpdateSchema,
    User,
    RegisterSchema,
)
from src.apps.users.utils import pwd_context
from src.core.exceptions import (
    AlreadyExistsException,
    DoesNotExistException,
    FriendRequestAlreadyHandled,
    InvalidCredentialsException,
    PermissionDeniedException,
    AlreadyActivatedAccountException,
)
from src.core.utils import get_object_by_id


class UserService:
    email_service_class = EmailService

    @classmethod
    async def _hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    async def register_user(cls, schema: RegisterSchema, session: AsyncSession) -> User:
        user_data = schema.dict()
        user_data.pop("password2")
        user_data["hashed_password"] = await cls._hash_password(
            password=user_data.pop("password")
        )
        email_result = await session.exec(
            select(User).where(User.username == user_data["username"])
        )
        if email_result.first():
            raise AlreadyExistsException("Email already in use!")
        username_result = await session.exec(
            select(User).where(User.username == user_data["username"])
        )
        if username_result.first():
            raise AlreadyExistsException("Username already taken!")
        new_user = User(**user_data)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @classmethod
    async def authenticate(
        cls, email: str, password: str, session: AsyncSession
    ) -> User:
        result = await session.exec(select(User).where(User.email == email))
        user: User = result.first()
        if user is None or not pwd_context.verify(password, user.hashed_password):
            raise InvalidCredentialsException("No matches with given token")
        return user

    @classmethod
    async def activate_account(
        cls,
        email: str,
        session: AsyncSession,
    ) -> None:
        user: User = (
            await session.exec(select(User).where(User.email == email))
        ).first()
        if user is None:
            raise DoesNotExistException("Invalid token")
        if user.is_active:
            raise AlreadyActivatedAccountException("User already activated his account")
        await session.execute(
            update(User).where(User.email == email).values(is_active=True)
        )
        await session.commit()

    @classmethod
    async def get_user_list(
        cls,
        session: AsyncSession,
    ) -> list[User]:
        return (await session.exec(select(User))).all()

    @classmethod
    async def get_user_by_id(
        cls,
        user_id: UUID,
        session: AsyncSession,
    ):
        return await get_object_by_id(Table=User, id=user_id, session=session)


class FriendService:
    @classmethod
    async def _find_friends(
        cls, user_id: UUID, friend_user_id: UUID, session: AsyncSession
    ) -> list[Union[Friend, None]]:
        friends = (
            await session.exec(
                select(Friend).where(
                    or_(
                        and_(
                            Friend.user_id == user_id,
                            Friend.friend_user_id == friend_user_id,
                        ),
                        and_(
                            Friend.friend_user_id == user_id,
                            Friend.user_id == friend_user_id,
                        ),
                    )
                )
            )
        ).all()
        return friends

    @classmethod
    async def _find_friend_by_id(
        cls, user_id: UUID, friend_id: UUID, session: AsyncSession
    ) -> Union[Friend, None]:
        friend = (
            await session.exec(
                select(Friend).where(
                    and_(
                        Friend.user_id == user_id,
                        Friend.id == friend_id,
                    )
                )
            )
        ).first()
        return friend

    @classmethod
    async def _find_friend_request(
        cls, user_id: UUID, friend_user_id: UUID, session: AsyncSession
    ):
        friend_request = (
            await session.exec(
                select(FriendRequest).where(
                    or_(
                        and_(
                            FriendRequest.from_user_id == user_id,
                            FriendRequest.to_user_id == friend_user_id,
                            FriendRequest.status == "PENDING",
                        ),
                        and_(
                            FriendRequest.from_user_id == friend_user_id,
                            FriendRequest.to_user_id == user_id,
                            FriendRequest.status == "PENDING",
                        ),
                    )
                )
            )
        ).first()
        return friend_request

    @classmethod
    async def create_friend(
        cls,
        user_id: UUID,
        friend_id: UUID,
        session: AsyncSession,
    ) -> Friend:
        friend1 = Friend(user_id=user_id, friend_user_id=friend_id)
        friend2 = Friend(user_id=friend_id, friend_user_id=user_id)
        session.add(friend1)
        session.add(friend2)
        await session.commit()
        await session.refresh(friend1)
        return friend1

    @classmethod
    async def delete_friend(
        cls,
        friend_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        friend = await get_object_by_id(Table=Friend, id=friend_id, session=session)
        if friend.user != request_user:
            raise PermissionDeniedException("Not authorized.")

        friends = await cls._find_friends(
            user_id=friend.user_id,
            friend_user_id=friend.friend_user_id,
            session=session,
        )
        for friend in friends:
            await session.delete(friend)
        await session.commit()
        return

    @classmethod
    async def filter_friend_list(
        cls,
        request_user: User,
        session: AsyncSession,
    ) -> list[Friend]:
        friends = (
            await session.exec(select(Friend).where(Friend.user_id == request_user.id))
        ).all()
        return friends

    @classmethod
    async def filter_friend_by_id(
        cls,
        friend_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> Friend:
        friend = await cls._find_friend_by_id(
            user_id=request_user.id, friend_id=friend_id, session=session
        )
        if friend is None:
            raise DoesNotExistException("Could not find friend with given id.")
        return friend

    @classmethod
    async def create_friend_request(
        cls,
        user_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        friends = await cls._find_friends(
            user_id=request_user.id, friend_user_id=user_id, session=session
        )
        if friends != []:
            raise AlreadyExistsException("You are already friends with this person.")

        request = await cls._find_friend_request(
            user_id=request_user.id, friend_user_id=user_id, session=session
        )
        if request is not None:
            raise AlreadyExistsException("Unhandled friend request exists.")

        request = FriendRequest(
            from_user_id=request_user.id, to_user_id=user_id, status="PENDING"
        )

        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request

    @classmethod
    async def update_friend_request(
        cls,
        schema: FriendRequestUpdateSchema,
        friend_request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        received_request = await cls.filter_received_friend_request_by_id(
            friend_request_id=friend_request_id,
            request_user=request_user,
            session=session,
        )
        if received_request.status != "PENDING":
            raise FriendRequestAlreadyHandled("Friend request was already handled.")
        update_data = schema.dict()
        await session.exec(
            update(FriendRequest)
            .where(FriendRequest.id == received_request.id)
            .values(**update_data)
        )
        await session.refresh(received_request)
        if received_request.status == "ACCEPTED":
            await cls.create_friend(
                user_id=request_user.id,
                friend_id=received_request.from_user_id,
                session=session,
            )
        return received_request

    @classmethod
    async def delete_friend_request(
        cls,
        friend_request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> FriendRequest:
        sent_request = await cls.filter_sent_friend_request_by_id(
            friend_request_id=friend_request_id,
            request_user=request_user,
            session=session,
        )
        await session.delete(sent_request)
        await session.commit()
        return

    @classmethod
    async def filter_received_friend_requests(
        cls,
        request_user: User,
        session: AsyncSession,
    ) -> list[FriendRequest]:
        received_requests = (
            await session.exec(
                select(FriendRequest).where(FriendRequest.to_user_id == request_user.id)
            )
        ).all()
        return received_requests

    @classmethod
    async def filter_received_friend_request_by_id(
        cls,
        friend_request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ):
        received_request = (
            await session.exec(
                select(FriendRequest).where(
                    and_(
                        FriendRequest.id == friend_request_id,
                        FriendRequest.to_user_id == request_user.id,
                    )
                )
            )
        ).first()
        if received_request is None:
            raise DoesNotExistException("Friend request with given id does not exist.")
        return received_request

    @classmethod
    async def filter_sent_friend_requests(
        cls,
        request_user: User,
        session: AsyncSession,
    ) -> list[FriendRequest]:
        sent_requests = (
            await session.exec(
                select(FriendRequest).where(
                    FriendRequest.from_user_id == request_user.id
                )
            )
        ).all()
        return sent_requests

    @classmethod
    async def filter_sent_friend_request_by_id(
        cls,
        friend_request_id: UUID,
        request_user: User,
        session: AsyncSession,
    ) -> FriendRequest:
        sent_request = (
            await session.exec(
                select(FriendRequest).where(
                    and_(
                        FriendRequest.id == friend_request_id,
                        FriendRequest.from_user_id == request_user.id,
                    )
                )
            )
        ).first()
        if sent_request is None:
            raise DoesNotExistException("Friend request with given id does not exist.")
        return sent_request
