import pytest
import httpx
import asyncio

host = "http://127.0.0.1:8001/api/v1/auth"


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
def wrong_pass_user_data():
    """Возвращает тестовые данные пользователя"""
    return {
        "mail": "demonuchy@gmail.com",
        "password": "WrongTestPassword123!",
    }


@pytest.fixture
def wrong_mail_user_data():
    """Возвращает тестовые данные пользователя"""
    return {
        "mail": "wrong_demonuchy@gmail.com",
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
def diff_device_headers():
    """Возвращает заголовки устройства"""
    return {
        "X-Device-Id": "diff_test-device-001",
        "X-Device-Name": "diff_Test Device"
    }




# РЕГИСТРАЦИЯ 
@pytest.mark.anyio
async def test_rgister(client, user_data, device_headers):
    
    response = await client.post(
        url=f"{host}/register",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 201

    # Повоторная регистрация не должна работать 
    response = await client.post(
        url=f"{host}/register",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 409


# ВХОД
@pytest.mark.anyio
async def test_login(client, user_data, wrong_pass_user_data, wrong_mail_user_data, device_headers, diff_device_headers):

    # Верные данные 
    response = await client.post(
        url=f"{host}/login",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 200

    # Вход с нового устройства
    response = await client.post(
        url=f"{host}/login",
        json=user_data,
        headers=diff_device_headers
    )
    assert response.status_code == 200


    # Неверный пароль 
    response = await client.post(
        url=f"{host}/login",
        json=wrong_pass_user_data,
        headers=device_headers
    )
    assert response.status_code == 401

    # Неверный mail
    response = await client.post(
        url=f"{host}/login",
        json=wrong_mail_user_data,
        headers=device_headers
    )
    assert response.status_code == 401


# Aунтификация
@pytest.mark.anyio
async def test_auth(client, user_data, device_headers):
    
    response = await client.post(
        url=f"{host}/login",
        json=user_data,
        headers=device_headers
    )
    assert response.status_code == 200

    response_data = response.json()
    access_token = response_data["data"]["access_token"]
    refresh_token = response_data["data"]["refresh_token"]

    response = await client.post(
        url=f"http://127.0.0.1:8080/api/v1/users",
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    response = await client.post(
        url=f"{host}/refresh",
        headers={"Authorization" : f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200

    response_data = response.json()
    access_token = response_data["data"]["access_token"]

    response = await client.post(
        url=f"http://127.0.0.1:8080/api/v1/users",
        headers={"Authorization" : f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    


    