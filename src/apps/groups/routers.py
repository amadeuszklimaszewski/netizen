from uuid import UUID
from fastapi import BackgroundTasks, Depends, status
from fastapi.routing import APIRouter
from fastapi_another_jwt_auth import AuthJWT

group_router = APIRouter(prefix="/groups")


@group_router.get()
async def get_groups():
    ...


@group_router.get()
async def get_group_by_id():
    ...


@group_router.post()
async def create_group():
    ...


@group_router.put()
async def update_group():
    ...


@group_router.delete()
async def delete_group():
    ...


@group_router.post()
async def join_to_group():
    ...


@group_router.post()
async def leave_group():
    ...
