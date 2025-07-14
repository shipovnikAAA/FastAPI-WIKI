import asyncpg
from logging import getLogger
from main.core.errors import DatabaseErrorHandler
from main.core.logger import setup_logging
from main.models.database import get_pool_data
from main.models.title import ReturnALLS, Paginated


setup_logging("ESP")
logger = getLogger(__name__)

async def return_sorted(table : str, conn : asyncpg.connection.Connection, params: Paginated) -> ReturnALLS:
    total : int | None = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
    
    query = f"SELECT * FROM {table}"
    if params.sort_by:
        if not params.sort_by.replace('_', '').isalnum():
            raise ValueError("Invalid sort_by parameter")
        query += f" ORDER BY {params.sort_by}"
        if params.sort_order:
            if params.sort_order and params.sort_order.lower() == 'desc':
                query += " DESC"
            else:
                query += " ASC"
        else:
            query += " ASC"
            params.sort_order = "ASC"
    else:
        query += " ORDER BY time DESC"
        params.sort_by = "time"
        params.sort_order = "DESC"
    
    query += " LIMIT $1 OFFSET $2"
    
    records = await conn.fetch(query, params.per_page, (params.page - 1) * params.per_page)
    return ReturnALLS(
        pagination = params,
        data = [dict(record) for record in records],
        total = total,
        total_pages = ((total or 0) + (params.per_page or 1) - 1) // (params.per_page or 1),
    )

async def get_all_esp_data_paginated(params: Paginated) -> ReturnALLS:
    """Возвращает данные с пагинацией и сортировкой"""
    logger.info(f"Получение данных всех esp (страница {params.page}, по {params.per_page} записей)")
    
    try:
        pool = await get_pool_data()
        async with pool.acquire() as conn:
            return await return_sorted("esp", conn, params)
    except Exception as e:
        logger.error(f"Ошибка при получении данных всех esp: {e}")
        raise

async def get_all_mac_data_paginated(params: Paginated) -> ReturnALLS:
    """Возвращает данные с пагинацией и сортировкой"""
    logger.info(f"Получение данных всех mac (страница {params.page}, по {params.per_page} записей)")
    
    try:
        pool = await get_pool_data()
        async with pool.acquire() as conn:
            return await return_sorted("uuids", conn, params)
    except Exception as e:
        logger.error(f"Ошибка при получении данных всех mac: {e}")
        raise

    
async def get_esp_by_id(uuid: str) -> dict | None:
    """Получает запись по ID"""
    logger.info(f"Получение записи по ID: {uuid}")
    try:
        pool = await get_pool_data()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                "SELECT * FROM esp WHERE uuid = $1", 
                uuid
            )
            return dict(record) if record else None
    except Exception as e:
        logger.error(f"Ошибка при получении записи: {e}")
        raise
