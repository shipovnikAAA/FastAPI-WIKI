from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from main.models.auth import Token, TokenData, UserInDB, UserCreate
from main.services.auth_service import (
    authenticate_user,
    get_user,
    create_user,
    create_access_token,
    create_refresh_token,
)
from main.core.config import JWT_CONFIG
from main.core.database_conf import get_database_connection_users
from logging import getLogger
from main.core.logger import setup_logging

setup_logging("auth")
logger = getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    """Получает текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if JWT_CONFIG.JWT_SECRET_KEY is None:
            raise credentials_exception

        # Добавляем проверку дополнительных полей токена
        payload = jwt.decode(
            token,
            JWT_CONFIG.JWT_SECRET_KEY,
            algorithms=[JWT_CONFIG.ALGORITHM],
            audience=JWT_CONFIG.TOKEN_AUDIENCE,
            issuer=JWT_CONFIG.TOKEN_ISSUER,
        )

        username = payload.get("sub")
        token_type = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception

        token_data = TokenData(username=str(username))
    except JWTError as e:
        logger.error(f"Ошибка проверки токена: {e}")
        raise credentials_exception

    if token_data.username is None:
        raise credentials_exception

    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Аутентификация пользователя и получение токенов."""
    logger.info(
        f"Попытка аутентификации пользователя: {form_data.username}, пароль: {form_data.password}"
    )

    tokens = await authenticate_user(form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return (
        tokens  # Теперь возвращаем словарь с access_token, refresh_token и token_type
    )


@router.post("/register", response_model=UserInDB)
async def register(user_data: UserCreate):
    user = await create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )
    return user


@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """Обновляет access token с помощью refresh token."""
    try:
        conn = await get_database_connection_users()
        try:
            # Проверяем refresh token в базе данных
            row = await conn.fetchrow(
                """
                SELECT user_id, expires_at 
                FROM refresh_tokens 
                WHERE token = $1
                """,
                refresh_token,
            )

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Недействительный refresh token",
                )

            if row["expires_at"] < datetime.now(timezone.utc):
                # Удаляем просроченный токен
                await conn.execute(
                    "DELETE FROM refresh_tokens WHERE token = $1", refresh_token
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token истек",
                )

            # Получаем пользователя
            user_row = await conn.fetchrow(
                """
                SELECT username 
                FROM users 
                WHERE id = $1
                """,
                row["user_id"],
            )

            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден",
                )

            # Создаем новые токены
            new_access_token = create_access_token({"sub": user_row["username"]})
            new_refresh_token, _ = await create_refresh_token(row["user_id"])

            # Удаляем старый refresh token
            await conn.execute(
                "DELETE FROM refresh_tokens WHERE token = $1", refresh_token
            )

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        finally:
            await conn.close()

    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена",
        )
