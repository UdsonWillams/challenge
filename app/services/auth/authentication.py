import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import get_settings
from app.database.models.base import Customer
from app.database.repositories.customer import CustomerRepository
from app.database.unit_of_work import UnitOfWorkConnection
from app.schemas.auth import RoleEnum, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.settings = get_settings()

    async def get_password_hash(self, password: str) -> str:
        return await asyncio.to_thread(pwd_context.hash, password)

    async def verify_password(self, plain: str, hashed: str) -> bool:
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

    async def create_access_token(
        self, subject: str, extra: Optional[Dict[str, Any]] = None
    ) -> str:
        now_utc = datetime.now(timezone.utc)
        to_encode: dict = {"sub": subject, "iat": int(now_utc.timestamp())}
        if extra:
            to_encode.update(extra)
        expire_dt = now_utc + self.settings.ACCESS_TOKEN_EXPIRE_DELTA
        to_encode["exp"] = int(expire_dt.timestamp())
        return await asyncio.to_thread(
            jwt.encode, to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM
        )

    async def decode_access_token(self, token: str) -> Optional[str]:
        try:
            payload = await asyncio.to_thread(
                jwt.decode,
                token,
                self.settings.SECRET_KEY,
                [self.settings.ALGORITHM],
            )
            return payload.get("sub")
        except JWTError:
            return None

    async def authenticate(
        self, email: str, password: str, uow: UnitOfWorkConnection
    ) -> Customer | None:
        repository = CustomerRepository(uow)
        user = await repository.get_user_by_email(email)
        if not user:
            return None
        if not await self.verify_password(password, user.password):
            return None
        return user

    async def issue_token(self, email: str, uow: UnitOfWorkConnection) -> Token:
        repo = CustomerRepository(uow)
        user = await repo.get_user_by_email(email)
        role = getattr(user, "role", RoleEnum.user) if user else RoleEnum.user
        token_str = await self.create_access_token(subject=email, extra={"role": role})
        return Token(access_token=token_str)


def get_auth_service() -> AuthService:
    return AuthService()
