from logging import getLogger
from main.core.errors import DatabaseErrorHandler
import asyncio
from main.core.logger import setup_logging
from main.models.database import get_pool_data

setup_logging("UUID")
logger = getLogger(__name__)

async def insert_mac_and_get_uuid(mac_address: str) -> str | None:
    """Асинхронно добавляет MAC-адрес и возвращает UUID, используя пул соединений."""
    logger.info(f"Inserting MAC {mac_address} and fetching UUID using pool...")
    try:
        pool = await get_pool_data()
        async with pool.acquire() as conn:
            try:
                uuid = await conn.fetchval(
                    """
                    INSERT INTO uuids (mac)
                    VALUES ($1)
                    RETURNING uuid;
                    """,
                    mac_address
                )
                logger.info(f"Inserted MAC: {mac_address}, got UUID: {uuid}")
                return str(uuid)
            except Exception as e:
                DatabaseErrorHandler.handle(e, "UUID")
    except Exception as e:
        logger.error(f"Database pool error: {e}")
        raise

async def get_uuid_by_mac(mac_address: str) -> str | None:
    """Асинхронно находит UUID по MAC-адресу, используя пул соединений."""
    logger.info(f"Searching UUID for MAC: {mac_address} using pool...")
    try:
        pool = await get_pool_data()
        async with pool.acquire() as conn:
            try:
                uuid = await conn.fetchval(
                    """
                    SELECT uuid FROM uuids
                    WHERE mac = $1
                    LIMIT 1;
                    """,
                    mac_address
                )
                if uuid:
                    logger.info(f"Found UUID: {uuid} for MAC: {mac_address}")
                    return str(uuid)
                logger.warning(f"MAC {mac_address} not found in database")
                return None
            except Exception as e:
                DatabaseErrorHandler.handle(e, "UUID")
    except Exception as e:
        logger.error(f"Database pool error: {e}")
        raise

if __name__ == "__main__":
    try:
        mac = "AA:BB:CC:DD:EE:FF"
        generated_uuid = asyncio.run(insert_mac_and_get_uuid(mac))
        print(f"Generated UUID: {generated_uuid}")
    except Exception as e:
        print(f"Failed: {e}")
