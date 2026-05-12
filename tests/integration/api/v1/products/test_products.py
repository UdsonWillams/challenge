import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_products(client: AsyncClient):
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient):
    resp = await client.get("/api/v1/products/1")
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_healthcheck(client: AsyncClient):
    resp = await client.get("/api/healthcheck")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_metrics(client: AsyncClient):
    resp = await client.get("/api/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text
