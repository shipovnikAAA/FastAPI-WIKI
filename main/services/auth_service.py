from datetime import datetime, timezone, timedelta
from main.models.auth import UserInDB, UserCreate
from main.core.database_conf import get_database_connection_data
from main.services.auth.password import hash_password, verify_password
from main.core.config import JWT_CONFIG
from jose import jwt
import uuid
from logging import getLogger
from main.core.logger import setup_logging

setup_logging("auth")
logger = getLogger(__name__)


async def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """Создает новый refresh token и сохраняет его в базе данных."""
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=JWT_CONFIG.REFRESH_TOKEN_EXPIRE_DAYS
    )

    conn = await get_database_connection_data()
    try:
        # Удаляем старые refresh токены пользователя
        await conn.execute("DELETE FROM refresh_tokens WHERE user_id = $1", user_id)

        # Сохраняем новый refresh token
        await conn.execute(
            """
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            """,
            user_id,
            token,
            expires_at,
        )
    finally:
        await conn.close()

    return token, expires_at


def create_access_token(data: dict) -> str:
    """Создает JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update(
        {
            "exp": expire,
            "type": "access",
            "aud": JWT_CONFIG.TOKEN_AUDIENCE,
            "iss": JWT_CONFIG.TOKEN_ISSUER,
            "jti": str(uuid.uuid4()),  # Добавляем уникальный идентификатор токена
        }
    )

    if JWT_CONFIG.JWT_SECRET_KEY is None:
        raise ValueError("JWT_SECRET_KEY must not be None")

    return jwt.encode(
        to_encode, JWT_CONFIG.JWT_SECRET_KEY, algorithm=JWT_CONFIG.ALGORITHM
    )


async def get_user(username: str) -> UserInDB | None:
    """Получает пользователя из базы данных по имени пользователя."""
    try:
        conn = await get_database_connection_data()
        try:
            row = await conn.fetchrow(
                """
                SELECT id, username, email, full_name, password_hash, 
                        disabled, created_at, last_login, role_id
                FROM users 
                WHERE username = $1
                """,
                username,
            )
            return UserInDB(**dict(row)) if row else None
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None


async def create_user(user_data: UserCreate) -> UserInDB | None:
    """Создает нового пользователя в базе данных."""
    try:
        conn = await get_database_connection_data()
        try:
            # Проверяем, существует ли пользователь
            exists = await conn.fetchrow(
                "SELECT username FROM users WHERE username = $1", user_data.username
            )
            if exists:
                return None  # Пользователь уже существует

            # Хешируем пароль и создаем пользователя
            hashed_password = hash_password(user_data.password)
            row = await conn.fetchrow(
                """
                INSERT INTO users (username, email, full_name, password_hash, disabled, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, username, email, full_name, password_hash, 
                            disabled, created_at, last_login
                """,
                user_data.username,
                user_data.email,
                user_data.full_name,
                hashed_password,
                user_data.disabled,
                datetime.now(timezone.utc),
            )
            return UserInDB(**dict(row)) if row else None

        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise


async def authenticate_user(username: str, password: str) -> dict | None:
    """Аутентифицирует пользователя и возвращает токены."""
    logger.info(f"Попытка аутентификации пользователя: {username}, пароль: {password}")
    try:
        user = await get_user(username)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Создаем access и refresh токены
        access_token = create_access_token({"sub": user.username})
        refresh_token, _ = await create_refresh_token(user.id)

        # Обновляем время последнего входа
        conn = await get_database_connection_data()
        try:
            await conn.execute(
                "UPDATE users SET last_login = $1 WHERE username = $2",
                datetime.now(timezone.utc),
                username,
            )
        finally:
            await conn.close()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except Exception as e:
        logger.error(f"Ошибка при аутентификации: {e}")
        return None
