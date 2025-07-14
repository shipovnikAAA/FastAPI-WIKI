from main.models import title
from main.services.esp.esp_uuid import insert_mac_and_get_uuid, get_uuid_by_mac
from main.services.esp.get_info import (
    get_all_esp_data_paginated,
    get_all_mac_data_paginated,
    get_esp_by_id,
)
from main.services.esp.put_title import insert_title_data
from main.models.title import ReturnALLS


class TitleService:
    @staticmethod
    async def put_esp(params: title.PUTTitle):
        """
        Асинхронно вставляет данные в таблицу esp.
        """
        return await insert_title_data(params)

    @staticmethod
    async def get_esp(params: title.GETTitlesParent):
        """
        Получает запись по ID
        """
        return await get_esp_by_id(params.title)

    @staticmethod
    async def get_all_esp(params: title.Paginated) -> ReturnALLS:
        """
        Получение всех ESP с пагинацией и сортировкой
        """
        return await get_all_esp_data_paginated(params)

    @staticmethod
    async def get_all_mac(params: title.Paginated):
        """
        Получение всех MAC с пагинацией и сортировкой
        """
        return await get_all_mac_data_paginated(params)
