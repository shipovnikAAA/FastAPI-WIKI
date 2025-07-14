import os
import secrets
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(__file__, "..", "..", "..", "migration", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
class ConfigDataBase:
    class ConfigDataBaseData:
        """Настройки базы данных."""
        DBNAME = os.getenv("DBNAME_DATA")
        DB_USER = os.getenv("DB_USER_DATA")
        DB_PASSWORD = os.getenv("DB_PASSWORD_DATA")
        DB_HOST = os.getenv("DB_HOST_DATA")
        DB_PORT = os.getenv("DB_PORT_DATA")
        MIN_SIZE : int = int(os.getenv("DB_MIN_SIZE_DATA", 1))
        MAX_SIZE : int = int(os.getenv("DB_MAX_SIZE_DATA", 10))

    class ConfigDataBaseUsers:
        """Настройки базы данных."""
        DBNAME = os.getenv("DBNAME_USERS")
        DB_USER = os.getenv("DB_USER_USERS")
        DB_PASSWORD = os.getenv("DB_PASSWORD_USERS")
        DB_HOST = os.getenv("DB_HOST_USERS")
        DB_PORT = os.getenv("DB_PORT_USERS")
        MIN_SIZE : int = int(os.getenv("DB_MIN_SIZE_USERS", 1))
        MAX_SIZE : int = int(os.getenv("DB_MAX_SIZE_USERS", 10))

class ConfigAPP:
    """Настройки приложения."""
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT : int = int(os.getenv("PORT", "5000"))
    RELOAD : bool = os.getenv("RELOAD", "False").lower() == "true"

class ConfigJWT:
    """Настройки JWT."""
    # Генерируем сложный ключ если не установлен
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))
    ALGORITHM : str = str(os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES : int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    TOKEN_AUDIENCE = os.getenv("TOKEN_AUDIENCE", "signal-api")
    TOKEN_ISSUER = os.getenv("TOKEN_ISSUER", "signal-auth")
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

APP_CONFIG = ConfigAPP()
DATABASE_DATA = ConfigDataBase.ConfigDataBaseData()
DATABASE_USERS = ConfigDataBase.ConfigDataBaseUsers()
JWT_CONFIG = ConfigJWT()