from main.core.logger import setup_logging
from logging import getLogger
from migration.database.core.database_conf import (
    get_database_connection_data,
    get_database_connection_users,
)


async def create_titles_table() -> None:
    """Создаёт таблицу esp с асинхронным подключением."""
    setup_logging("ESP")
    logger = getLogger(__name__)

    logger.info("db esp creating")
    try:
        conn = await get_database_connection_data()
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS titles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL UNIQUE,
                    parent INT NOT NULL DEFAULT -1,
                    path TEXT NOT NULL UNIQUE,
                    time TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            logger.info("Таблица titles создана/проверена")

        except Exception as e:
            logger.error(f"Ошибка при создании таблицы esp: {e}", exc_info=True)
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}", exc_info=True)
        raise


async def create_texts_table() -> None:
    """Создаёт таблицу UUIDS с асинхронным подключением."""
    setup_logging("UUID")
    logger = getLogger(__name__)

    logger.info("db uuid creating")
    try:
        conn = await get_database_connection_data()
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS texts (
                    id SERIAL PRIMARY KEY,
                    title_id INT NOT NULL,
                    text TEXT NOT NULL,
                    FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE
                );
            """
            )
            logger.info("Таблица uuids создана/проверена")

        except Exception as e:
            logger.error(f"Ошибка при создании таблицы uuids: {e}", exc_info=True)
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}", exc_info=True)
        raise


async def create_permisions_table() -> None:
    """Создаёт таблицу roles с асинхронным подключением."""
    setup_logging("auth")
    logger = getLogger(__name__)

    logger.info("db roles creating")
    try:
        conn = await get_database_connection_users()
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
                );"""
            )
            # Вставляем предопределенные роли, если их нет
            await conn.execute(
                """
                INSERT INTO roles (name, description) VALUES
                ('admin', 'Администратор с полными правами: чтение, редактирование, создание'),
                ('user', 'Обычный пользователь: только чтение'),
                ('editor', 'Редактор: чтение и редактирование'),
                ('creator', 'Создатель: чтение и создание')
                ON CONFLICT (name) DO NOTHING;"""
            )
            user_role_id = await conn.fetchval(
                "SELECT id FROM roles WHERE name = 'user'"
            )
            if user_role_id is None:
                raise RuntimeError("Default role 'user' not found in 'roles' table.")

            # Add the role_id column to the users table if it doesn't exist, nullable for now.
            await conn.execute(
                """
                ALTER TABLE users ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES roles(id);
                """
            )
            # Set the role for existing users who don't have one.
            await conn.execute(
                "UPDATE users SET role_id = $1 WHERE role_id IS NULL", user_role_id
            )

            # Now, set the DEFAULT value for new users and the NOT NULL constraint.
            await conn.execute(
                f"ALTER TABLE users ALTER COLUMN role_id SET DEFAULT {user_role_id}"
            )
            await conn.execute("ALTER TABLE users ALTER COLUMN role_id SET NOT NULL")
            logger.info(
                "Таблицы roles и users (с role_id) созданы/проверены и заполнены базовыми ролями."
            )

        except Exception as e:
            logger.error(
                f"Ошибка при создании таблиц roles/user_roles: {e}", exc_info=True
            )
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}", exc_info=True)
        raise


async def create_users_table() -> None:
    """Создаёт таблицу users с асинхронным подключением."""
    setup_logging("auth")
    logger = getLogger(__name__)

    logger.info("db users creating")
    try:
        conn = await get_database_connection_users()
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(128) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    full_name VARCHAR(100),
                    disabled BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_login TIMESTAMPTZ
                )
                """
            )
            logger.info("Таблица users создана/проверена")

        except Exception as e:
            logger.error(f"Ошибка при создании таблицы users: {e}", exc_info=True)
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}", exc_info=True)
        raise
