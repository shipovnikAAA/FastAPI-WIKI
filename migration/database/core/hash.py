import bcrypt
from typing import Optional
from logging import getLogger
from migration.database.core.database_conf import PEPPER

logger = getLogger(__name__)

def hash_password(password: str) -> str:
    """
    Хеширует пароль используя bcrypt.
    
    Args:
        password: Пароль в открытом виде
    
    Returns:
        str: Хешированный пароль
    """
    peppered_password = password.encode('utf-8') + PEPPER.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(peppered_password, salt)
    return password_hash.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешу.
    
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль из БД
    
    Returns:
        bool: True если пароль верный
    """
    peppered_password = plain_password.encode('utf-8') + PEPPER.encode('utf-8')
    try:
        return bcrypt.checkpw(
            peppered_password,
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Ошибка при проверке пароля: {e}")
        return False