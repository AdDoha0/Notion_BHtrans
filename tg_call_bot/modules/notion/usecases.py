import os, logging
from modules.openai.client import process_audio_to_comment
from share.utils import cleanup_temp_files

logger = logging.getLogger(__name__)
TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "temp")

async def transcribe_file(bot, file_id: str, filename_hint: str = "audio.mp3") -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    cleanup_temp_files(TEMP_DIR)  # твоя очистка старше 60 мин
    tg_file = await bot.get_file(file_id)
    ext = filename_hint.split(".")[-1] if "." in filename_hint else "mp3"
    path = os.path.join(TEMP_DIR, f"{file_id}.{ext}")
    await bot.download_file(tg_file.file_path, path)
    try:
        text = await process_audio_to_comment(path)
        return text or ""
    finally:
        try:
            os.remove(path)
        except Exception as e:
            logger.warning(f"Temp cleanup fail: {e}")
