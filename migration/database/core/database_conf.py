import asyncpg
import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(__file__, "..", "..", "..", "..", "migration", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class ConfigDataBaseData:
    """Настройки базы данных."""
    DBNAME = os.getenv("DBNAME_DATA")
    DB_USER = os.getenv("DB_USER_DATA")
    DB_PASSWORD = os.getenv("DB_PASSWORD_DATA")
    DB_HOST = os.getenv("DB_HOST_DATA")
    DB_PORT = os.getenv("DB_PORT_DATA")
    MIN_SIZE : int = int(os.getenv("DB_MIN_SIZE_DATA", 1))
    MAX_SIZE : int = int(os.getenv("DB_MAX_SIZE_DATA", 10))

DATABASE_DATA = ConfigDataBaseData()

async def get_database_pool_data() -> asyncpg.Pool:
    """Создает и возвращает пул соединений с базой данных."""
    return await asyncpg.create_pool(
        database=DATABASE_DATA.DBNAME,
        user=DATABASE_DATA.DB_USER,
        password=DATABASE_DATA.DB_PASSWORD,
        host=DATABASE_DATA.DB_HOST,
        port=DATABASE_DATA.DB_PORT,
        min_size=10,
        max_size=100,
        max_queries=50000,
        max_inactive_connection_lifetime=60,
        timeout=30
    )

async def get_database_connection_data() -> asyncpg.Connection:
    """Создает и возвращает соединение с базой данных."""
    return await asyncpg.connect(
        database=DATABASE_DATA.DBNAME,
        user=DATABASE_DATA.DB_USER,
        password=DATABASE_DATA.DB_PASSWORD,
        host=DATABASE_DATA.DB_HOST,
        port=DATABASE_DATA.DB_PORT,
    )

class ConfigDataBaseUsers:
    """Настройки базы данных."""
    DBNAME = os.getenv("DBNAME_USERS")
    DB_USER = os.getenv("DB_USER_USERS")
    DB_PASSWORD = os.getenv("DB_PASSWORD_USERS")
    DB_HOST = os.getenv("DB_HOST_USERS")
    DB_PORT = os.getenv("DB_PORT_USERS")
    MIN_SIZE : int = int(os.getenv("DB_MIN_SIZE_USERS", 1))
    MAX_SIZE : int = int(os.getenv("DB_MAX_SIZE_USERS", 10))

DATABASE_USERS = ConfigDataBaseUsers()

async def get_database_pool_users() -> asyncpg.Pool:
    """Создает и возвращает пул соединений с базой данных."""
    return await asyncpg.create_pool(
        database=DATABASE_USERS.DBNAME,
        user=DATABASE_USERS.DB_USER,
        password=DATABASE_USERS.DB_PASSWORD,
        host=DATABASE_USERS.DB_HOST,
        port=DATABASE_USERS.DB_PORT,
        min_size=10,
        max_size=100,
        max_queries=50000,
        max_inactive_connection_lifetime=60,
        timeout=30
    )

async def get_database_connection_users() -> asyncpg.Connection:
    """Создает и возвращает соединение с базой данных."""
    return await asyncpg.connect(
        database=DATABASE_USERS.DBNAME,
        user=DATABASE_USERS.DB_USER,
        password=DATABASE_USERS.DB_PASSWORD,
        host=DATABASE_USERS.DB_HOST,
        port=DATABASE_USERS.DB_PORT,
    )