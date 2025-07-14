import httpx
from fastapi import HTTPException, status
from typing import Optional
from main.models.auth import UserInDB
from main.core.config import JWT_CONFIG
from logging import getLogger

logger = getLogger(__name__)

async def validate_token(token: str) -> Optional[UserInDB]:
    """Проверяет токен через auth сервис."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                f"https://192.168.0.133:5001/api/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return UserInDB(**user_data)
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                logger.error(f"Ошибка при проверке токена: {response.status_code} - {response.text}")
                return None
                
    except httpx.HTTPError as e:
        logger.error(f"HTTP ошибка при проверке токена: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке токена: {e}")
        return None