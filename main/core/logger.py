from logging.handlers import RotatingFileHandler
from logging import StreamHandler, basicConfig, INFO

def setup_logging(log : str):
    """Общая конфигурация логгера для всех скриптов."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = fr".\main\logs\{log}.log"

    # Настройка обработчиков
    handlers = [
        RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        ),
        StreamHandler(),
    ]

    basicConfig(
        level=INFO,
        format=log_format,
        handlers=handlers,
    )