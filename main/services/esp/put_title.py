import asyncpg
from logging import getLogger
from main.core.config import DATABASE_DATA
from main.core.errors import DatabaseErrorHandler
from main.models import title
from main.core.logger import setup_logging
from main.core.database_conf import configurate_database
from main.core.database_conf import get_database_pool_data
import os

setup_logging("ESP")
logger = getLogger(__name__)

async def get_parents_by_title(title_name: str) -> list[dict] | None:
    """
    Возвращает всех родителей для заданного title, включая сам title.
    """
    logger.info(f"Получение всех родителей для title: {title_name}")
    try:
        pool = await get_database_pool_data()
        async with pool.acquire() as conn:
            # Используем рекурсивный CTE для получения всех родителей
            records = await conn.fetch(
                """
                WITH RECURSIVE parents AS (
                    SELECT id, title, parent, path, time
                    FROM titles
                    WHERE title = $1

                    UNION ALL

                    SELECT t.id, t.title, t.parent, t.path, t.time
                    FROM titles t
                    INNER JOIN parents p ON t.id = p.parent
                )
                SELECT id, title, parent, path, time FROM parents;
                """,
                title_name
            )
            if records:
                return [dict(record) for record in records]
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении родителей для title {title_name}: {e}")
        raise


async def insert_title_data(params: title.PUTTitle) -> dict[str, str | float] | None:
    """Асинхронно вставляет данные в таблицу esp с использованием пула соединений."""
    logger.info(f"Вставка данных в таблицу esp: {params.title}")
    try:
        pool = await get_database_pool_data()
        async with pool.acquire() as conn:
            parents = await get_parents_by_title(params.title)
            print(parents)
            path = await configurate_database(params.title).return_path()
            try:
                await conn.execute(
                    """
                    INSERT INTO title (title, parent, path)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    params.title,
                    params.parent,
                    path,
                )
                await configurate_database(params.title).create_directories()
                logger.info(f"Данные успешно добавлены для UUID: {params.parent}")
                return {
                    "title": params.title,
                    "parent": params.parent,
                    "path": path,
                }
            except Exception as e:
                DatabaseErrorHandler.handle(e, "UUID")
    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}")
        raise
