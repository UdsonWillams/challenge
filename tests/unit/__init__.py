import pytest

from app.database.repositories.customer import CustomerRepository
from app.exceptions.exceptions import NotFoundError
from app.schemas.domain.customers.input import CreateCustomer
from app.services.auth.authentication import AuthService
from app.services.domain.customer import CustomerService


@pytest.mark.asyncio
async def test_auth_service_hash_password():
    service = AuthService()
    hashed = await service.get_password_hash("test123!")
    assert hashed != "test123!"
    assert await service.verify_password("test123!", hashed)
    assert not await service.verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_auth_service_token_roundtrip():
    service = AuthService()
    token = await service.create_access_token("test@mail.com", extra={"role": "user"})
    assert token is not None
    email = await service.decode_access_token(token)
    assert email == "test@mail.com"


@pytest.mark.asyncio
async def test_auth_service_refresh_token():
    service = AuthService()
    token = await service.create_refresh_token("test@mail.com")
    email = await service.decode_refresh_token(token)
    assert email == "test@mail.com"

    email_access = await service.decode_access_token(token)
    assert email_access is None


@pytest.mark.asyncio
async def test_customer_service_create(uow, async_session):
    service = CustomerService(uow)
    payload = CreateCustomer(
        email="service_test@mail.com",
        password="StrongPass1!",
        name="Service Test",
    )
    result = await service.create_customer(payload)
    assert result["email"] == "service_test@mail.com"
    assert result["name"] == "Service Test"


@pytest.mark.asyncio
async def test_customer_service_get_by_id_not_found(uow):
    service = CustomerService(uow)
    with pytest.raises(NotFoundError):
        await service.get_by_id("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_customer_repository_get_by_email(uow):
    repo = CustomerRepository(uow)
    result = await repo.get_user_by_email("nonexistent@mail.com")
    assert result is None
