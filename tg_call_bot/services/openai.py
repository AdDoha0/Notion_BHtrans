from openai import AsyncOpenAI
from config import OPENAI_KEY
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_KEY)

def get_promt() -> str:
    """Получает промт из файла"""
    try:
        # Определяем путь к файлу промта относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        promt_path = os.path.join(current_dir, "..", "promt.txt")
        
        with open(promt_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении промта: {e}")
        return "Ты HR-эксперт. Проанализируй звонок с водителем и дай профессиональный отчет."

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
            model="gpt-4o",  # Используем доступную модель
            messages=[
                {"role": "system", "content": get_promt()},
                {"role": "user", "content": f"Проанализируй этот звонок с водителем:\n\n{message}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        logger.info("Успешно получен ответ от GPT")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при создании GPT ответа: {e}")
        raise


async def process_audio_to_comment(file_path: str) -> str:
    """Полный процесс: транскрибация + анализ GPT"""
    try:
        # Транскрибируем аудио
        transcribed_text = await transcription(file_path)
        logger.info(f"Транскрибированный текст: {transcribed_text[:100]}...")
        
        # Анализируем через GPT
        gpt_analysis = await create_gptAnswer(transcribed_text)
        
        return gpt_analysis
    except Exception as e:
        logger.error(f"Ошибка при обработке аудио: {e}")
        raise


