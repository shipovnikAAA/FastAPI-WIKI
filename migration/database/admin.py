from datetime import datetime, timezone
from main.models.auth import UserInDB
from migration.database.core.database_conf import get_database_connection_users
from migration.database.core.hash import hash_password
from logging import getLogger
from main.core.logger import setup_logging
from main.models.roles import UserRole

setup_logging("auth")
logger = getLogger(__name__)
# logger = getLogger('auth')

async def create_Sadovnikov_user() -> UserInDB | None:
    """Создает первого пользователя Sadovnikov если он не существует."""
    try:
        conn = await get_database_connection_users()
        try:
            # Проверяем существование пользователя Sadovnikov
            row = await conn.fetchrow(
                "SELECT username FROM users WHERE username = $1", "Sadovnikov"
            )
            if row:
                logger.info("Пользователь Sadovnikov уже существует")
                return None

            # Создаем пользователя Sadovnikov с захешированным паролем
            hashed_password = hash_password("СЫЫР")  # password = "СЫЫР"
            logger.info("Создание пользователя Sadovnikov")
            row = await conn.fetchrow(
                """
                INSERT INTO users (username, email, full_name, password_hash, disabled, created_at, role_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, username, email, full_name, password_hash, 
                            disabled, created_at, last_login, role_id
                """,
                "Sadovnikov",
                "Sadovnikov@example.com",
                "СЫЫРОК",
                hashed_password,
                False,
                datetime.now(timezone.utc),
                UserRole.ADMIN.value
            )
            return UserInDB(**dict(row)) if row else None

        except Exception as e:
            logger.error(f"Ошибка при создании пользователя Sadovnikov: {e}")
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")