from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    """Модель JWT токена."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Данные для создания токена."""

    username: str | None = None
    password: str | None = None


class UserBase(BaseModel):
    """Базовая модель пользователя."""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False


class User(UserBase):
    """Модель пользователя для ответов API."""

    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserInDB(User):
    """Модель пользователя для работы с базой данных."""

    id: int
    password_hash: str
    role_id: int
