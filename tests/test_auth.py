import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    """Тест регистрации нового пользователя."""
    response = await client.post("/users/", json={
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["role"] == "user"


@pytest.mark.anyio
async def test_register_existing_email(client: AsyncClient, test_user):
    """Тест попытки регистрации с уже существующим email."""
    response = await client.post("/users/", json={
        "email": test_user["email"],
        "password": "another_password",
        "role": "user"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.anyio
async def test_login_success(client: AsyncClient, test_user):
    """Тест успешного входа и получения токенов."""
    response = await client.post("/token", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Тест входа с неверным паролем."""
    response = await client.post("/token", data={
        "username": test_user["email"],
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_login_nonexistent_user(client: AsyncClient):
    """Тест входа с несуществующим email."""
    response = await client.post("/token", data={
        "username": "nonexistent@example.com",
        "password": "any_password"
    })
    assert response.status_code == 401


@pytest.mark.anyio
async def test_protected_route_without_token(client: AsyncClient):
    """Тест доступа к защищённому маршруту без токена."""
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_protected_route_with_valid_token(client: AsyncClient, test_user):
    """Тест доступа к /users/me с валидным токеном."""
    # Получаем токен
    login_resp = await client.post("/token", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    token = login_resp.json()["access_token"]

    # Запрос с токеном
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]


@pytest.mark.anyio
async def test_protected_route_with_invalid_token(client: AsyncClient):
    """Тест доступа с некорректным токеном."""
    response = await client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_refresh_token(client: AsyncClient, test_user):
    """Тест обновления access токена по refresh токену."""
    # Получаем пару токенов
    login_resp = await client.post("/token", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    # Обновляем access токен
    refresh_resp = await client.post("/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens
    assert new_tokens["refresh_token"] == refresh_token
    