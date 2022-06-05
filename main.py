from fastapi import FastAPI, Request, status
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi_another_jwt_auth.exceptions import AuthJWTException

from src.apps.users.routers import user_router
from src.apps.jwt.routers import jwt_router
from src.apps.groups.routers import group_router
from src.core.exceptions import (
    APIException,
    DoesNotExistException,
    PermissionDeniedException,
)

app = FastAPI(title="Netizen", description="API for a social network", version="1.0")

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(jwt_router)
router.include_router(group_router)
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello world"}


# ----- Exception handlers -----


@app.exception_handler(DoesNotExistException)
def api_error_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


@app.exception_handler(PermissionDeniedException)
def api_error_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)}
    )


@app.exception_handler(APIException)
def api_error_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
