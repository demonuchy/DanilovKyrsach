import pytest
import httpx
import asyncio

host = "http://127.0.0.1:8080/api/v1"


@pytest.fixture
async def client():
    """Создает и закрывает HTTP клиент"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client  


@pytest.fixture
def user_data():
    """Возвращает тестовые данные пользователя"""
    return {
        "mail": "demonuchy@gmail.com",
        "password": "TestPassword123!",
    }

@pytest.fixture
def device_headers():
    """Возвращает заголовки устройства"""
    return {
        "X-Device-Id": "test-device-001",
        "X-Device-Name": "Test Device"
        }


@pytest.mark.anyio
async def test_create_recipes(client, user_data, device_headers):

    # Верные данные 
    response = await client.post(
        url=f"{host}/auth/login",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 200

    response_data = response.json()
    access_token = response_data["data"]["access_token"]
    refresh_token = response_data["data"]["refresh_token"]

    # Create recipes
    response = await client.post(
        url=f"{host}/recipes",
        json={
            "title" : "Recipe 1", 
            "ingredients": [
                    {"name":"курица"},
                    {"name":"соль"}
            ],
            "tags": [

            ]
        },
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 201


    response = await client.post(
        url=f"{host}/recipes",
        json={
            "title" : "Recipe 2", 
            "ingredients": [
                    {"name":"курица"},
                    {"name":"соль"},
                    {"name" :"капуста"}
            ],
            "tags": [
                {"name" : "быстро"}
            ]
        },
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 201


    response = await client.post(
        url=f"{host}/recipes",
        json={
            "title" : "Recipe 3", 
            "ingredients": [
                    {"name":"курица"},
                    {"name":"яйца"}
            ],
            "tags": [
                {"name" : "горячее"}
            ]
        },
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_search_recipes(client, user_data, device_headers):
    response = await client.post(
        url=f"{host}/auth/login",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 200

    response_data = response.json()
    access_token = response_data["data"]["access_token"]
    refresh_token = response_data["data"]["refresh_token"]

    response = await client.get(
        url=f"{host}/recipes",
        params={
            "ingredient_name": ["курица"],
            "tag_name": ["быстро"]
        },
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 200


    response = await client.get(
        url=f"{host}/recipes",
        params={
            "ingredient_name": ["курица", "яйца"],
        },
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    response = await client.get(
        url=f"{host}/recipes/2",
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 200
