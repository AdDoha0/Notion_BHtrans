from openai import AsyncOpenAI
from share.config import OPENAI_KEY
import asyncio
import os
import logging

from share.promt_utils import get_promt

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_KEY)


async def transcription(file_path: str) -> str:
    """Транскрибирует аудиофайл в текст"""
    logger.info(f"Транскрибируем аудиофайл в текст")
    try:
        with open(file_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        logger.info(f"Успешно транскрибирован файл: {file_path}")
        return response.text
    except Exception as e:
        logger.error(f"Ошибка при транскрибации файла {file_path}: {e}")
        raise

async def create_gptAnswer(message: str) -> str:
    """Создает ответ GPT на основе транскрибированного текста"""
    logger.info(f"Создаем ответ GPT на основе транскрибированного текста")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": get_promt()},
                {"role": "user", "content": f"Проанализируй этот звонок с водителем:\n\n{message}"}
            ],
            max_tokens=2000
        )
        logger.info("Успешно получен ответ от GPT")
        result = response.choices[0].message.content
        logger.info(f"Результат GPT: {len(result) if result else 0} символов")
        return result or ""
    except Exception as e:
        logger.error(f"Ошибка при создании GPT ответа: {e}")
        raise


async def process_audio_to_comment(file_path: str) -> str:
    """Полный процесс: транскрибация + анализ GPT"""
    try:
        # Транскрибируем аудио
        transcribed_text = await transcription(file_path)
        logger.info(f"Транскрибированный текст: {transcribed_text[:100]}...")
        
        if not transcribed_text or transcribed_text.strip() == "":
            logger.warning("Пустой результат транскрибации")
            return "Не удалось распознать речь в аудиозаписи"
        
        # Анализируем через GPT
        gpt_analysis = await create_gptAnswer(transcribed_text)
        
        if not gpt_analysis or gpt_analysis.strip() == "":
            logger.warning("Пустой результат от GPT")
            return f"Транскрибированный текст: {transcribed_text}"
        
        return gpt_analysis
    except Exception as e:
        logger.error(f"Ошибка при обработке аудио: {e}")
        raise


