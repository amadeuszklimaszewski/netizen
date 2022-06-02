import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_another_jwt_auth import AuthJWT

from src.apps.users.services import UserService
from src.apps.users.models import UserOutputSchema, RegisterSchema


@pytest.fixture
def user_register_data() -> dict[str, str]:
    return {
        "first_name": "name",
        "last_name": "name",
        "username": "username",
        "email": "testuser@google.com",
        "password": "test12345",
        "password2": "test12345",
        "birthday": "2000-01-01",
    }


@pytest_asyncio.fixture
async def register_user(
    user_register_data: dict[str, str], session: AsyncSession
) -> UserOutputSchema:
    schema = RegisterSchema(**user_register_data)
    return await UserService.register_user(schema=schema, session=session)


@pytest.fixture
def user_bearer_token_header(register_user: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(subject=register_user.json())
    return {"Authorization": f"Bearer {access_token}"}
