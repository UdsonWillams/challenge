import pytest
from httpx import AsyncClient

from app.database.models.base import Customer


async def _get_token_for_customer(client, customer):
    resp = await client.post(
        "/api/v1/auth/token",
        json={"email": customer.email, "password": customer.plain_password},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.mark.asyncio
async def test_create(client: AsyncClient, customer_admin: Customer):
    payload = {
        "email": "user_integration@example.com",
        "password": "StrongPass1!",
        "name": "User Integration",
    }
    headers = await _get_token_for_customer(client, customer_admin)
    resp = await client.post("/api/v1/customers", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_customer(client: AsyncClient, customer: Customer):
    headers = await _get_token_for_customer(client, customer)
    resp = await client.get(f"/api/v1/customers/{customer.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(customer.id)
    assert data["email"] == customer.email


@pytest.mark.asyncio
async def test_list_customers(client: AsyncClient, customer_admin: Customer, some_customers: list[Customer]):
    headers = await _get_token_for_customer(client, customer_admin)
    resp = await client.get("/api/v1/customers", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_update_customer(client: AsyncClient, customer: Customer):
    headers = await _get_token_for_customer(client, customer)
    payload = {"name": "Updated Name", "email": "updated@mail.com"}
    resp = await client.put(f"/api/v1/customers/{customer.id}", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_delete_customer(client: AsyncClient, customer: Customer, customer_admin: Customer):
    headers = await _get_token_for_customer(client, customer_admin)
    resp = await client.delete(f"/api/v1/customers/{customer.id}", headers=headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/customers/{customer.id}", headers=headers)
    assert get_resp.status_code == 404
