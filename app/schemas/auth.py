from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class UserBase(BaseModel):
    email: EmailStr


class UserLogin(UserBase):
    password: str


class AuthenticatedUser(UserBase):
    id: UUID
    full_name: str | None = None
    is_active: bool = True
    role: RoleEnum = RoleEnum.user


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    sub: str | None = None


__all__ = [
    "UserBase",
    "UserLogin",
    "Token",
    "RefreshToken",
    "TokenData",
    "RoleEnum",
    "AuthenticatedUser",
]
