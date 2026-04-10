from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.models import User
from app.database import get_db
from app.core.security import get_password_hash, get_current_user
from app.core.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя. Email должен быть уникальным. По умолчанию роль 'user'.",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Email уже зарегистрирован"}
    }
)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"Зарегистрирован новый пользователь: {db_user.email}, роль: {db_user.role}")
    return db_user


@router.get(
    "/",
    response_model=list[schemas.User],
    summary="Получить список пользователей",
    description="Возвращает список пользователей с пагинацией.",
)
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


@router.get(
    "/me",
    response_model=schemas.User,
    summary="Информация о текущем пользователе",
    description="Возвращает данные аутентифицированного пользователя.",
    responses={401: {"description": "Не авторизован"}}
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    summary="Получить пользователя по ID",
    description="Возвращает данные конкретного пользователя.",
    responses={404: {"description": "Пользователь не найден"}}
)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user