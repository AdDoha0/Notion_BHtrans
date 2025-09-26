from openai import AsyncOpenAI
from share.config import OPENAI_KEY
import logging

from share.promt_utils import get_promt_call_analyze

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
        return response
    except Exception as e:
        logger.error(f"Ошибка при транскрибации файла {file_path}: {e}")
        raise


async def create_gptAnswer(
        message: str,
        system_promt: str,
        model: str = "gpt-4o",
        max_tokens: int = None,
                           ) -> str:
    """Создает ответ GPT на основе транскрибированного текста"""
    logger.info(f"Создаем ответ GPT на основе транскрибированного текста")
    try:
        completion_params = {
            "model": model, 
            "messages": [
                {"role": "system", "content": system_promt},
                {"role": "user", "content": f"{message}"}
            ]
        }
        
        # Добавляем max_tokens только если он указан
        if max_tokens is not None:
            completion_params["max_tokens"] = max_tokens
            
        response = await client.chat.completions.create(**completion_params)
        logger.info("Успешно получен ответ от GPT")
        result = response.choices[0].message.content
        logger.info(f"Результат GPT: {len(result) if result else 0} символов")
        return result or ""
    except Exception as e:
        logger.error(f"Ошибка при создании GPT ответа: {e}")
        raise




async def analyze_transcribed_text(transcribed_text: str, system_promt: str, model: str = "gpt-4o", max_tokens: int = None) -> str:
    """Анализирует транскрибированный текст через GPT"""
    try:
        logger.info(f"Анализируем транскрибированный текст: {transcribed_text[:100]}...")
        
        if not transcribed_text or transcribed_text.strip() == "":
            logger.warning("Пустой текст для анализа")
            return "Не удалось распознать речь в аудиозаписи"
        
        # Анализируем через GPT
        gpt_analysis = await create_gptAnswer(
            transcribed_text,
            system_promt=system_promt,
            model=model,
            max_tokens=max_tokens
        )
        
        if not gpt_analysis or gpt_analysis.strip() == "":
            logger.warning("Пустой результат от GPT")
            return f"Транскрибированный текст: {transcribed_text}"
        
        return gpt_analysis
    except Exception as e:
        logger.error(f"Ошибка при анализе текста: {e}")
        raise





