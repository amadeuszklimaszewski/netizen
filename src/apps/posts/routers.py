from uuid import UUID
from typing import Union

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.connection import get_db
from src.apps.users.models import User
from src.dependencies.users import authenticate_user, get_user_or_none
from src.apps.posts.models import (
    PostInputSchema,
    PostOutputSchema,
    CommentInputSchema,
    CommentOutputSchema,
    ReactionOutputSchema,
)
from src.apps.groups.services import GroupService


posts = APIRouter()
