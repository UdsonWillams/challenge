from fastapi import APIRouter, Depends

from app.database.unit_of_work import UnitOfWorkConnection, get_uow
from app.exceptions.exceptions import UnauthorizedError
from app.schemas.auth import Token, UserLogin
from app.services.auth.authentication import AuthService

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token)
async def login(form: UserLogin, uow: UnitOfWorkConnection = Depends(get_uow)):
    service = AuthService()
    user = await service.authenticate(form.email, form.password, uow)
    if not user:
        raise UnauthorizedError
    return await service.issue_token(user.email, uow)
