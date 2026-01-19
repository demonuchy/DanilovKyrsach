import pytest
import httpx


@pytest.mark.anyio
async def test_health_nginx():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8080/health")
        assert response.status_code == 200


@pytest.mark.anyio
async def test_health_auth():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8001/health")
        assert response.status_code == 200


@pytest.mark.anyio
async def test_health_recipe():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8002/health")
        assert response.status_code == 200


