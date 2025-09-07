from openai import OpenAI, AsyncOpenAI
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Добавляем родительскую директорию в путь для импорта
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)

async def create_response(messages: str) -> str:
    logger.info(f"Запрос к OpenAI: {messages}")
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "user", "content": messages}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        answer = completion.choices[0].message.content
        logger.info(f"Ответ от OpenAI: {answer}")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return f"Произошла ошибка: {str(e)}"
    


async def transcribe_audio(audio: bytes) -> str:
    try:
        completion = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
        return completion.text  
    except Exception as e:  
        logger.error(f"Ошибка при транскрибации аудио: {e}")
        return f"Произошла ошибка: {str(e)}"


