from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app import schemas
from app.schemas.token import RefreshTokenRequest
from app.models import User, RefreshToken
from app.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    save_refresh_token,
    oauth2_scheme
)
from app.config import settings
from app.core.logger import logger

router = APIRouter(tags=["authentication"])


@router.post(
    "/token",
    response_model=schemas.Token,
    summary="Вход и получение токенов",
    description="Аутентифицирует пользователя по email и паролю. Возвращает access_token и refresh_token.",
    responses={
        200: {"description": "Успешный вход", "content": {"application/json": {"example": {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}}}},
        401: {"description": "Неверный email или пароль"}
    }
)


async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя по email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа для email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Пользователь {user.email} вошёл в систему")

    # Создание access токена
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "scopes": user.scopes, "role": user.role},
        expires_delta=access_token_expires
    )

    # Создание refresh токена
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=refresh_token_expires
    )
    await save_refresh_token(db, user.id, refresh_token, refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post(
    "/refresh",
    response_model=schemas.Token,
    summary="Обновить access токен",
    description="Принимает refresh_token и возвращает новую пару токенов.",
    responses={
        200: {"description": "Токен обновлён"},
        401: {"description": "Refresh токен недействителен или истёк"}
    }
)

async def refresh_access_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = data.refresh_token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        if payload.get("type") != "refresh":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Ошибка декодирования refresh токена: {e}")
        raise credentials_exception

    # Проверяем refresh token в базе
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if (
        db_token is None
        or db_token.revoked
        or db_token.expires_at < datetime.utcnow()
    ):
        logger.warning("Refresh токен не найден в БД, отозван или истёк")
        raise credentials_exception

    # Получаем пользователя
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        logger.warning(f"Пользователь с email {email} не найден при обновлении токена")
        raise credentials_exception

    logger.info(f"Refresh токен использован для пользователя {user.email}")

    # Создаём новый access токен
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "scopes": user.scopes, "role": user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = data.refresh_token
    print(f"Received refresh token: {refresh_token[:20]}...")  # Отладка

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Декодирование токена
    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        print(f"Decoded payload: {payload}")  # Отладка
    except JWTError as e:
        print(f"JWT decode error: {e}")  # Отладка
        raise credentials_exception

    # 2. Проверка типа токена
    if payload.get("type") != "refresh":
        print(f"Token type is not refresh: {payload.get('type')}")  # Отладка
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        print("No 'sub' in payload")  # Отладка
        raise credentials_exception
    print(f"Email from token: {email}")  # Отладка

    # 3. Проверка в базе данных
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if db_token is None:
        print("Refresh token not found in DB")  # Отладка
        raise credentials_exception
    if db_token.revoked:
        print("Refresh token is revoked")  # Отладка
        raise credentials_exception
    if db_token.expires_at < datetime.utcnow():
        print(f"Refresh token expired at {db_token.expires_at}")  # Отладка
        raise credentials_exception

    # 4. Поиск пользователя
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        print(f"User with email {email} not found")  # Отладка
        raise credentials_exception

    print("All checks passed, generating new access token")  # Отладка

    # 5. Создание нового access токена
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "scopes": user.scopes, "role": user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }