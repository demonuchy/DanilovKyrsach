import pytest
import httpx

HOST = "http://127.0.0.1:8080/api/v1"


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


@pytest.fixture
async def auth_tokens(client, user_data, device_headers):
    """Получает токены аутентификации"""
    response = await client.post(
        url=f"{HOST}/auth/login",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 200
    
    response_data = response.json()
    return {
        "access_token": response_data["data"]["access_token"],
        "refresh_token": response_data["data"]["refresh_token"]
    }


@pytest.mark.anyio
async def test_create_recipes(client, auth_tokens):
    """Тест создания рецептов"""
    
    # Создание первого рецепта
    response = await client.post(
        url=f"{HOST}/recipes",
        json={
            "title": "Recipe 1",
            "ingredients": [
                {"name": "курица"},
                {"name": "соль"}
            ],
            "tags": []
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 201
    
    # Создание второго рецепта
    response = await client.post(
        url=f"{HOST}/recipes",
        json={
            "title": "Recipe 2",
            "ingredients": [
                {"name": "соль"},
                {"name": "капуста"}
            ],
            "tags": [
                {"name": "быстро"}
            ]
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 201
    
    # Создание третьего рецепта
    response = await client.post(
        url=f"{HOST}/recipes",
        json={
            "title": "Recipe 3",
            "ingredients": [
                {"name": "курица"},
                {"name": "яйца"}
            ],
            "tags": [
                {"name": "горячее"}
            ]
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_search_recipes(client, auth_tokens):
    """Тест поиска и удаления рецептов"""
    
    # Поиск по ингредиенту "курица" и тегу "быстро"
    response = await client.get(
        url=f"{HOST}/recipes",
        params={
            "ingredient_name": ["курица"],
            "tag_name": ["быстро"]
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 404
    
    # Поиск по ингредиентам "капуста" и "соль"
    response = await client.get(
        url=f"{HOST}/recipes",
        params={
            "ingredient_name": ["капуста", "соль"],
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 200

    response_data = response.json()

    response = await client.get(
        url=f"{HOST}/recipes/{response_data['data']['recipes'][0].get('id')}",
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 200
    
    # Удаление найденных рецептов
    for recipe in response_data['data']['recipes']:
        response = await client.delete(
            url=f"{HOST}/recipes/{recipe.get('id')}",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        assert response.status_code == 200
    
    # Поиск по ингредиенту "курица" и тегу "горячее"
    response = await client.get(
        url=f"{HOST}/recipes",
        params={
            "ingredient_name": ["курица"],
            "tag_name": ["горячее"]
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 200


    # Удаление найденных рецептов
    response_data = response.json()
    for recipe in response_data['data']['recipes']:
        response = await client.delete(
            url=f"{HOST}/recipes/{recipe.get('id')}",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        assert response.status_code == 200
    
    # Поиск только по ингредиенту "курица"
    response = await client.get(
        url=f"{HOST}/recipes",
        params={
            "ingredient_name": ["курица"],
        },
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
    )
    assert response.status_code == 200
    
    # Удаление найденных рецептов
    response_data = response.json()
    for recipe in response_data['data']['recipes']:
        response = await client.delete(
            url=f"{HOST}/recipes/{recipe.get('id')}",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        assert response.status_code == 200
    