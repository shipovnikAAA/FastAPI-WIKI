from main.core.config import APP_CONFIG
import uvicorn
from main.core.logger import setup_logging
from logging import getLogger
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

setup_logging("API")
logger = getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    if APP_CONFIG.HOST and APP_CONFIG.PORT:
        logger.info(f"Запуск сервера {APP_CONFIG.HOST}:{APP_CONFIG.PORT}")
        uvicorn.run(
            "main.api.app:APP",
            host=APP_CONFIG.HOST,
            port=APP_CONFIG.PORT,
            reload=APP_CONFIG.RELOAD
        )
        logger.info("Server started")
    else:
        logger.error("Не указаны APP_HOST и APP_PORT в конфигурации. Проверьте настройки.")
        raise ValueError("Не указаны APP_HOST и APP_PORT в конфигурации. Проверьте настройки.")