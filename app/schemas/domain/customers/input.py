import re

from pydantic import BaseModel, EmailStr, field_validator


class CreateCustomer(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        return v.strip().lower() if v else v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 150:
            raise ValueError("Name must be at most 150 characters")
        return v


class UpdateCustomer(BaseModel):
    name: str | None = None
    password: str | None = None
    email: EmailStr | None = None

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 150:
            raise ValueError("Name must be at most 150 characters")
        return v
