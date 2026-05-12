import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/healthcheck")
    assert response.status_code == 200
    content = response.json()
    assert "status" in content
    assert "database" in content
    assert "redis" in content
