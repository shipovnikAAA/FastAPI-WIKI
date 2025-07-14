from fastapi import APIRouter, Depends, HTTPException, Query, status
from main.models import title as esp_model
from main.services.esp_service import TitleService
from main.models.auth import UserInDB
from logging import getLogger
from main.core.logger import setup_logging
from typing import Annotated

setup_logging("esp")
logger = getLogger(__name__)

router = APIRouter(
    prefix="/api/esp",
    tags=["esp"]
)

# @router.post("/")
# async def post_esp(params: esp_model.POSTEsp):
#     try:
#         return {"uuid": await ESPService.post_esp(params)}
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/")
async def put_esp(params: esp_model.PUTTitle):
    try:
        return await TitleService.put_esp(params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/")
async def get_esp(params: esp_model.GETTitlesParent = Depends()):
    return await TitleService.get_esp(params)

# @router.get("/uuid")
# async def get_uuid(params: esp_model.GETUUID = Depends()):
#     try:
#         return {"uuid": await ESPService.get_uuid(params)}
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/all/esp", response_model=esp_model.ReturnALLS)
async def get_all_esp(
    params: esp_model.Paginated = Depends()
):
    """Получить все ESP устройства с пагинацией и сортировкой."""
    try:
        return await TitleService.get_all_esp(
            params
        )
    except Exception as e:
        logger.error(f"Ошибка при получении всех ESP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/mac", response_model=esp_model.ReturnALLS)
async def get_all_mac(
    params: esp_model.Paginated = Depends()
):
    try:
        return await TitleService.get_all_mac(params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
