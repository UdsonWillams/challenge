import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_health_check(
    client: TestClient,
):
    response = await client.get(
        "/api/healthcheck",
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "status" in content
    assert content["status"] == "OK"
