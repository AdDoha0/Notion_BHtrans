from openai import AsyncOpenAI
from share.config import OPENAI_KEY
import asyncio
from logger import logger
from modules.openai.client import create_gptAnswer

client = AsyncOpenAI(api_key=OPENAI_KEY)

def get_promt() -> str:
    with open("promt.txt", "r") as file:
        return file.read()




async def transcription(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text

# async def create_gptAnswer(message: str) -> str:
#     """Создает ответ GPT на основе транскрибированного текста"""
#     logger.info(f"Создаем ответ GPT на основе транскрибированного текста")
#     try:
#         response = await client.chat.completions.create(
#             model="gpt-5",  # Используем доступную модель
#             messages=[
#                 {"role": "system", "content": "Раздеели это транкрипцию на спикеров"},
#                 {"role": "user", "content": f"Проанализируй этот звонок с водителем:\n\n{message}"}
#             ],
#         )
#         logger.info("Успешно получен ответ от GPT")
#         return response.choices[0].message.content
#     except Exception as e:
#         logger.error(f"Ошибка при создании GPT ответа: {e}")
#         raise





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

print(asyncio.run(process_audio_to_comment("../mock_audio/hr4.mp3")))

