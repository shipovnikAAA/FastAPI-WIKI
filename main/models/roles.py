from enum import Enum, auto

class UserRole(Enum):
    ADMIN = auto()
    USER = auto()
    MODERATOR = auto()
    
    @classmethod
    def get_role_id(cls, role: 'UserRole') -> int:
        """Возвращает ID роли для базы данных"""
        return {
            cls.ADMIN: 1,
            cls.USER: 2,
            cls.MODERATOR: 3
        }[role]
    
    @classmethod
    def from_role_id(cls, role_id: int) -> 'UserRole | None':
        """Создает enum из ID роли"""
        return {
            1: cls.ADMIN,
            2: cls.USER,
            3: cls.MODERATOR
        }.get(role_id)