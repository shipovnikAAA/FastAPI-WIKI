from main.models import audio
import aiofiles
import os
from logging import getLogger
from main.core.logger import setup_logging
from main.core.database_conf import configurate_database

setup_logging("AUDIO")
logger = getLogger(__name__)

class AudioService:
    @staticmethod
    async def post_audio(params: audio.POSTAudio):
        """Асинхронно сохраняет MP3 файл."""
        try:
            audio_path = await configurate_database(params.uuid).return_path_audio()
            
            file_path = os.path.join(audio_path, f"{params.file.filename}")
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await params.file.read()
                await out_file.write(content)
            
            logger.info(f"Файл {params.file.filename} успешно сохранен для UUID: {params.uuid}")
            return {
                "uuid": params.uuid,
                "filename": params.file.filename,
                "path": file_path
            }
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            raise

    @staticmethod
    async def get_audio(params: audio.GETAudio):
        """Получение информации об аудиофайлах для заданного UUID."""
        try:
            audio_path = await configurate_database(params.uuid).return_path_audio()
            
            if not os.path.exists(audio_path):
                return {"files": []}
            
            files = [f for f in os.listdir(audio_path) if f.endswith('.mp3')]
            return {
                "uuid": params.uuid,
                "files": files,
                "path": audio_path
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации об аудиофайлах: {e}")
            raise