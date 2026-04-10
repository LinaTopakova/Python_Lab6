import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.core.security import get_password_hash

# Тестовая БД в памяти (или файловая, но лучше в памяти)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def client():
    # Создаём асинхронный движок для тестовой БД
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Подменяем зависимость get_db на тестовую сессию
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Очистка
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(client: AsyncClient):
    """Создаёт тестового пользователя и возвращает его данные."""
    user_data = {
        "email": "test@example.com",
        "password": "secret123",
        "role": "user"
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    return user_data