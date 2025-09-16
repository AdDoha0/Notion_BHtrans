from openai import AsyncOpenAI
from config import OPENAI_KEY
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_KEY)

def get_promt() -> str:
    """Получает полный промт из двух файлов"""
    try:
        # Определяем путь к файлам промта относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_prompt_path = os.path.join(current_dir, "..", "prompt_main.txt")
        template_path = os.path.join(current_dir, "..", "template_response.txt")
        
        main_prompt = ""
        template = ""
        
        # Читаем основной промт
        with open(main_prompt_path, "r", encoding="utf-8") as file:
            main_prompt = file.read()
            
        # Читаем шаблон ответа
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
            
        return f"{main_prompt}\n\n{template}"
    except Exception as e:
        logger.error(f"Ошибка при чтении промта: {e}")
        return "Ты HR-эксперт. Проанализируй звонок с водителем и дай профессиональный отчет."

def get_main_prompt() -> str:
    """Получает только основной промт"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_prompt_path = os.path.join(current_dir, "..", "prompt_main.txt")
        
        # Проверяем существование файла
        if not os.path.exists(main_prompt_path):
            # Создаем файл с дефолтным содержимым
            default_prompt = "Ты HR-эксперт. Проанализируй звонок с водителем и дай профессиональный отчет."
            with open(main_prompt_path, "w", encoding="utf-8") as file:
                file.write(default_prompt)
            logger.info(f"Создан файл основного промпта: {main_prompt_path}")
            return default_prompt
        
        with open(main_prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении основного промта: {e}")
        return "Ты HR-эксперт. Проанализируй звонок с водителем и дай профессиональный отчет."

def get_response_template() -> str:
    """Получает только шаблон ответа"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "..", "template_response.txt")
        
        # Проверяем существование файла
        if not os.path.exists(template_path):
            # Создаем файл с дефолтным содержимым
            default_template = "Стандартный шаблон ответа недоступен."
            with open(template_path, "w", encoding="utf-8") as file:
                file.write(default_template)
            logger.info(f"Создан файл шаблона ответа: {template_path}")
            return default_template
        
        with open(template_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении шаблона ответа: {e}")
        return "Стандартный шаблон ответа недоступен."

def save_main_prompt(content: str) -> bool:
    """Сохраняет основной промт"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_prompt_path = os.path.join(current_dir, "..", "prompt_main.txt")
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(main_prompt_path), exist_ok=True)
        
        with open(main_prompt_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Основной промт успешно сохранен: {main_prompt_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении основного промта: {e}")
        return False

def save_response_template(content: str) -> bool:
    """Сохраняет шаблон ответа"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "..", "template_response.txt")
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        with open(template_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Шаблон ответа успешно сохранен: {template_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении шаблона ответа: {e}")
        return False

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


