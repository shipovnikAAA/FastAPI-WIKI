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
    
class DataBase:
    class data:
        class PostgreSQL:
            @staticmethod
            async def get_pool() -> asyncpg.Pool:
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
            @staticmethod
            async def get_connection() -> asyncpg.Connection:
                """Создает и возвращает соединение с базой данных."""
                return await asyncpg.connect(
                    database=DATABASE_DATA.DBNAME,
                    user=DATABASE_DATA.DB_USER,
                    password=DATABASE_DATA.DB_PASSWORD,
                    host=DATABASE_DATA.DB_HOST,
                    port=DATABASE_DATA.DB_PORT,
                )
        class MySQL:
            @staticmethod
            async def get_pool():
                ...
            @staticmethod
            async def get_connection():
                ...
        class SQLite:
            @staticmethod
            async def get_pool():
                ...
            @staticmethod
            async def get_connection():
                ...
    class Users:
        class PostgreSQL:
            @staticmethod
            async def get_pool() -> asyncpg.Pool:
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
            @staticmethod
            async def get_connection() -> asyncpg.Connection:
                """Создает и возвращает соединение с базой данных."""
                return await asyncpg.connect(
                    database=DATABASE_USERS.DBNAME,
                    user=DATABASE_USERS.DB_USER,
                    password=DATABASE_USERS.DB_PASSWORD,
                    host=DATABASE_USERS.DB_HOST,
                    port=DATABASE_USERS.DB_PORT,
                )
        class MySQL:
            @staticmethod
            async def get_pool():
                ...
            @staticmethod
            async def get_connection():
                ...
        class SQLite:
            @staticmethod
            async def get_pool():
                ...
            @staticmethod
            async def get_connection():
                ...

async def get_pool(db, table):
    match db.lower():
        case 'sqlite':
            if table.lower() == 'users':
                connector = DataBase.Users.SQLite.get_pool()
            else:
                connector = DataBase.data.SQLite.get_pool()
        case 'mysql':
            if table.lower() == 'users':
                connector = DataBase.Users.MySQL.get_pool()
            else:
                connector = DataBase.data.MySQL.get_pool()
        case 'postgresql':
            if table.lower() == 'users':
                connector = DataBase.Users.PostgreSQL.get_pool()
            else:
                connector = DataBase.data.PostgreSQL.get_pool()
        case _:
            raise ValueError("Unknown DB type")
    return connector
async def get_connection(db, table):
    match db.lower():
        case 'sqlite':
            if table.lower() == 'users':
                connector = DataBase.Users.SQLite.get_connection()
            else:
                connector = DataBase.data.SQLite.get_connection()
        case 'mysql':
            if table.lower() == 'users':
                connector = DataBase.Users.MySQL.get_connection()
            else:
                connector = DataBase.data.MySQL.get_connection()
        case 'postgresql':
            if table.lower() == 'users':
                connector = DataBase.Users.PostgreSQL.get_connection()
            else:
                connector = DataBase.data.PostgreSQL.get_connection()
        case _:
            raise ValueError("Unknown DB type")
    return connector