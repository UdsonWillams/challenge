import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, customer):
    resp = await client.post(
        "/api/v1/auth/token",
        json={"email": customer.email, "password": customer.plain_password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, customer):
    resp = await client.post(
        "/api/v1/auth/token",
        json={"email": customer.email, "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/token",
        json={"email": "nonexistent@mail.com", "password": "pass123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, customer):
    login_resp = await client.post(
        "/api/v1/auth/token",
        json={"email": customer.email, "password": customer.plain_password},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_access_protected_without_token(client: AsyncClient):
    resp = await client.get("/api/v1/customers")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_access_protected_invalid_token(client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    resp = await client.get("/api/v1/customers", headers=headers)
    assert resp.status_code == 401
