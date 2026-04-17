import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_shape(client):
    response = await client.get("/api/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime" in data
    assert "version" in data
    assert isinstance(data["uptime"], float)
