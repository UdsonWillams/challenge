from pydantic import BaseModel, EmailStr


class CreateCustomer(BaseModel):
    email: EmailStr
    password: str
    name: str


class UpdateCustomer(BaseModel):
    name: str | None = None
    password: str | None = None
    email: EmailStr | None = None
