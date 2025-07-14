from main.core.logger import setup_logging
from logging import getLogger
from main.core.database_conf import get_database_connection_data
from datetime import datetime, timezone

setup_logging("auth")
logger = getLogger(__name__)

logger.info("db creating")

async def create_school_tables() -> None:
    """Создаёт таблицы для работы со школами."""
    logger.info("Создание таблиц для школ")
    try:
        conn = await get_database_connection_data()
        try:
            # Создаем таблицу стран
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(128) NOT NULL UNIQUE,
                    code CHAR(2) NOT NULL UNIQUE,  -- ISO 3166-1 alpha-2
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Создаем таблицу городов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(128) NOT NULL,
                    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(name, country_id)
                )
            """)

            # Создаем таблицу школ с внешними ключами на города
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id SERIAL PRIMARY KEY,
                    city_id INTEGER NOT NULL REFERENCES cities(id),
                    email VARCHAR(100) NOT NULL UNIQUE,
                    full_name VARCHAR(100),
                    disabled BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_login TIMESTAMPTZ,
                    uuid UUID,
                    FOREIGN KEY (uuid) REFERENCES uuids(uuid) ON DELETE CASCADE
                )
            """)

            # Добавляем базовые страны и города
            await conn.execute("""
                INSERT INTO countries (name, code) 
                VALUES ('Россия', 'RU'), ('Казахстан', 'KZ'), ('Беларусь', 'BY')
                ON CONFLICT (code) DO NOTHING
            """)

            # Получаем ID России для добавления городов
            russia_id = await conn.fetchval("SELECT id FROM countries WHERE code = 'RU'")
            if russia_id:
                # Добавляем основные города России
                await conn.execute("""
                    INSERT INTO cities (name, country_id) 
                    VALUES 
                        ('Москва', $1),
                        ('Санкт-Петербург', $1),
                        ('Новосибирск', $1),
                        ('Екатеринбург', $1),
                        ('Казань', $1)
                    ON CONFLICT (name, country_id) DO NOTHING
                """, russia_id)

            logger.info("Таблицы для школ успешно созданы/обновлены")

        except Exception as e:
            logger.error(f"Ошибка при создании таблиц школ: {e}", exc_info=True)
            raise
        finally:
            await conn.close()

    except Exception as e:
        logger.critical(f"Ошибка подключения к БД: {e}", exc_info=True)
        raise