from asyncpg.exceptions import StringDataRightTruncation, UniqueViolationError
from main.core.logger import setup_logging
from logging import getLogger


class DatabaseErrorHandler:
    """Класс для обработки ошибок PostgreSQL без дублирования логов."""

    @staticmethod
    def handle(error: Exception, context: str) -> None:
        """Обрабатывает ошибку и вызывает соответствующее исключение."""
        exc_class = DatabaseErrorHandler._map_error(error)
        setup_logging(context)
        logger = getLogger(__name__)
        logger.error("Database error: %s", str(error))
        raise exc_class(error) from None

    @staticmethod
    def _map_error(error: Exception) -> type:
        """Определяет класс исключения по типу ошибки."""
        if isinstance(error, StringDataRightTruncation): 
            return DatabaseErrorHandler.MacLengthError
        elif isinstance(error, UniqueViolationError):
            return DatabaseErrorHandler.MacAlreadyExistsError
        return DatabaseErrorHandler.GenericDBError

    class MacLengthError(Exception):
        def __init__(self, original_error):
            msg = "Некорректная длина MAC-адреса (требуется 17 символов)"
            super().__init__(f"{msg}. Детали: {str(original_error)}")

    class MacAlreadyExistsError(Exception):
        def __init__(self, original_error):
            msg = "MAC-адрес уже существует в базе"
            super().__init__(f"{msg}. Детали: {str(original_error)}")

    class GenericDBError(Exception):
        def __init__(self, original_error):
            msg = "Ошибка базы данных"
            super().__init__(f"{msg}: {str(original_error)}")


class ValidationErrorHandler:
    @staticmethod
    def handle(error: Exception, context: str) -> None:
        setup_logging(context)
        logger = getLogger(__name__)
        logger.error("Database error: %s", str(error))
        raise ValidationErrorHandler.ValidationError(error) from None

    class ValidationError(ValueError):
        """Исключение для ошибок валидации."""
        def __init__(self, original_error):
            msg = "Ошибка валидации данных"
            super().__init__(f"{msg}: {str(original_error)}")
