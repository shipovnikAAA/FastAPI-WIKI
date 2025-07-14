from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from main.models.auth import UserInDB
from main.services.auth_client import validate_token
from logging import getLogger

logger = getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class get_oauth2_scheme():
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        """Получает текущего пользователя из токена через auth сервис."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        user = await validate_token(token)
        if not user:
            raise credentials_exception
            
        return user

    @staticmethod
    async def get_current_active_user(
        current_user: UserInDB = Depends(get_current_user)
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user