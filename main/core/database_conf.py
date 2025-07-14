import os
import asyncpg
from main.core.config import DATABASE_DATA, DATABASE_USERS

class configurate_database:
    """
    Класс для конфигурации базы данных.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self.data_dir = os.path.abspath(os.path.join(__file__, "..", "..", "..", "database", "data"))
        self.path = os.path.join(self.data_dir, f"{title}")

    async def create_directories(self) -> None:
        """
        Создаёт необходимые директории для хранения данных.
        """
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    async def return_path(self) -> str:
        """
        Возвращает путь к директории для хранения данных.
        """
        return self.path
    
    
async def get_database_pool_data() -> asyncpg.Pool:
    """Создает и возвращает пул соединений с базой данных."""
    print(DATABASE_DATA.DBNAME, DATABASE_DATA.DB_USER, DATABASE_DATA.DB_PASSWORD, DATABASE_DATA.DB_HOST, DATABASE_DATA.DB_PORT)
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
