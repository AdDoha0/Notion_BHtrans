import os, logging
from modules.openai.client import transcription, analyze_transcribed_text
from share.utils import cleanup_temp_files
from share.config import MAX_AUDIO_SIZE_MB

logger = logging.getLogger(__name__)
TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "temp")

async def transcribe_file(bot, file_id: str, filename_hint: str = "audio.mp3", system_promt: str = None) -> str:
    """Скачивает файл из Telegram, транскрибирует его и анализирует через GPT"""
    os.makedirs(TEMP_DIR, exist_ok=True)
    cleanup_temp_files(TEMP_DIR)  # очистка старше 60 мин
    tg_file = await bot.get_file(file_id)
    
    # Проверяем размер файла
    file_size_mb = tg_file.file_size / (1024 * 1024) if tg_file.file_size else 0
    if file_size_mb > MAX_AUDIO_SIZE_MB:
        logger.warning(f"Файл слишком большой: {file_size_mb:.1f}MB (максимум {MAX_AUDIO_SIZE_MB}MB)")
        return f"❌ Файл слишком большой ({file_size_mb:.1f}MB). Максимальный размер: {MAX_AUDIO_SIZE_MB}MB"
    ext = filename_hint.split(".")[-1] if "." in filename_hint else "mp3"
    path = os.path.join(TEMP_DIR, f"{file_id}.{ext}")
    await bot.download_file(tg_file.file_path, path)
    try:
        # Сначала транскрибируем
        transcribed_text = await transcription(path)
        if not transcribed_text:
            return ""
        
        # Если есть system_promt, анализируем через GPT
        if system_promt:
            analyzed_text = await analyze_transcribed_text(transcribed_text, system_promt)
            return analyzed_text or transcribed_text
        
        # Иначе возвращаем просто транскрибированный текст
        return transcribed_text
    finally:
        try:
            os.remove(path)
        except Exception as e:
            logger.warning(f"Temp cleanup fail: {e}") 