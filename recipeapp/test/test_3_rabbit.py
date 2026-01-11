import pytest
import httpx
import asyncio



@pytest.mark.anyio
async def test_health_auth():
    """Простой тест health эндпоинтов"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8001/api/v1/auth/rebbit/test")
        assert response.status_code == 200