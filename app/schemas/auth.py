from enum import Enum
from typing import Optional
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
    full_name: Optional[str] = None
    is_active: bool = True
    role: RoleEnum = RoleEnum.user


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


__all__ = [
    "UserBase",
    "UserLogin",
    "Token",
    "TokenData",
    "RoleEnum",
    "AuthenticatedUser",
]
