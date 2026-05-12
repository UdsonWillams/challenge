import asyncio
from datetime import UTC, datetime
from typing import Any

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

    async def _encode_token(self, subject: str, expire_delta, extra: dict[str, Any] | None = None) -> str:
        now_utc = datetime.now(UTC)
        to_encode: dict = {"sub": subject, "iat": int(now_utc.timestamp())}
        if extra:
            to_encode.update(extra)
        expire_dt = now_utc + expire_delta
        to_encode["exp"] = int(expire_dt.timestamp())
        to_encode["type"] = extra.get("type", "access") if extra else "access"
        return await asyncio.to_thread(jwt.encode, to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM)

    async def create_access_token(self, subject: str, extra: dict[str, Any] | None = None) -> str:
        merged = extra or {}
        merged["type"] = "access"
        return await self._encode_token(subject, self.settings.ACCESS_TOKEN_EXPIRE_DELTA, merged)

    async def create_refresh_token(self, subject: str, extra: dict[str, Any] | None = None) -> str:
        merged = extra or {}
        merged["type"] = "refresh"
        return await self._encode_token(subject, self.settings.REFRESH_TOKEN_EXPIRE_DELTA, merged)

    async def decode_access_token(self, token: str) -> str | None:
        try:
            payload = await asyncio.to_thread(
                jwt.decode,
                token,
                self.settings.SECRET_KEY,
                [self.settings.ALGORITHM],
            )
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    async def decode_refresh_token(self, token: str) -> str | None:
        try:
            payload = await asyncio.to_thread(
                jwt.decode,
                token,
                self.settings.SECRET_KEY,
                [self.settings.ALGORITHM],
            )
            if payload.get("type") != "refresh":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    async def authenticate(self, email: str, password: str, uow: UnitOfWorkConnection) -> Customer | None:
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
        access_token = await self.create_access_token(subject=email, extra={"role": role})
        refresh_token = await self.create_refresh_token(subject=email, extra={"role": role})
        return Token(access_token=access_token, refresh_token=refresh_token)


def get_auth_service() -> AuthService:
    return AuthService()
