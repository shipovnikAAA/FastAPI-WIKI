import asyncpg
from migration.database.core.database_conf import get_database_pool_data
_db_pool: asyncpg.Pool | None = None

async def init_pool():
    global _db_pool
    _db_pool = await get_database_pool_data()

async def get_pool() -> asyncpg.Pool:
    if _db_pool is None:
        raise RuntimeError("Pool is not initialized!")
    return _db_pool

async def close_pool():
    if _db_pool:
        await _db_pool.close()