from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.database.unit_of_work import UnitOfWorkConnection, get_uow
from app.exceptions.exceptions import UnauthorizedError
from app.schemas.auth import RefreshToken, Token, UserLogin
from app.services.auth.authentication import AuthService

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token, status_code=HTTPStatus.OK)
async def login(form: UserLogin, uow: UnitOfWorkConnection = Depends(get_uow)):
    service = AuthService()
    user = await service.authenticate(form.email, form.password, uow)
    if not user:
        raise UnauthorizedError("Invalid email or password")
    return await service.issue_token(user.email, uow)


@router.post("/refresh", response_model=Token, status_code=HTTPStatus.OK)
async def refresh_token(payload: RefreshToken, uow: UnitOfWorkConnection = Depends(get_uow)):
    service = AuthService()
    email = await service.decode_refresh_token(payload.refresh_token)
    if not email:
        raise UnauthorizedError("Invalid or expired refresh token")
    return await service.issue_token(email, uow)
