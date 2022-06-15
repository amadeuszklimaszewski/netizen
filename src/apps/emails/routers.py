from fastapi import APIRouter, status


email_router = APIRouter()


@email_router.post(
    "/confirm/{token}",
    status_code=status.HTTP_200_OK,
)
async def confirm_account(
    token: str,
):
    ...
