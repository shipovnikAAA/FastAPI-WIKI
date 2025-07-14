import asyncpg
from main.core.database_conf import get_database_pool_data, get_database_pool_users
_db_pool_data: asyncpg.Pool | None = None
_db_pool_users: asyncpg.Pool | None = None

async def init_pool_data():
    global _db_pool_data
    _db_pool_data = await get_database_pool_data()

async def get_pool_data() -> asyncpg.Pool:
    if _db_pool_data is None:
        raise RuntimeError("Pool is not initialized!")
    return _db_pool_data

async def close_pool_data():
    if _db_pool_data:
        await _db_pool_data.close()
        
async def init_pool_users():
    global _db_pool_users
    _db_pool_users = await get_database_pool_users()

async def get_pool_users() -> asyncpg.Pool:
    if _db_pool_users is None:
        raise RuntimeError("Pool is not initialized!")
    return _db_pool_users

async def close_pool_users():
    if _db_pool_users:
        await _db_pool_users.close()