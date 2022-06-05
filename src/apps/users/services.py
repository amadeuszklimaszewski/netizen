from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apps.users.models import (
    User,
    UserOutputSchema,
    RegisterSchema,
)
from src.apps.users.utils import pwd_context
from src.core.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException,
)


class UserService:
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
    def send_activation_email(cls, email: str):
        ...
