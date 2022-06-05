from uuid import UUID
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.exceptions import DoesNotExistException, InvalidTableException


async def get_object_by_id(Table: SQLModel, id: UUID | int, session: AsyncSession):
    try:
        object = (await session.exec(select(Table).where(Table.id == id))).first()
        if object is None:
            raise DoesNotExistException("Object with given id does not exist")
        return object
    except TypeError as exc:
        raise InvalidTableException("Invalid table name")
