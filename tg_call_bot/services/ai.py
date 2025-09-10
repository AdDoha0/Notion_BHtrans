from openai import OpenAI, AsyncOpenAI
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


from config import OPENAI_API_KEY

client = AsyncOpenAI(
    base_url="https://api.langdock.com/openai/eu/v1",
    api_key=OPENAI_API_KEY,
)

async def create_response(messages: str) -> str:
    logger.info(f"Запрос к OpenAI: {messages}")
    promt = """


""" + messages
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "user", "content": promt}
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
    


# # Тестовая функция для транскрибации аудио
# async def transcribe_audio_test():
#     with open("/home/user/my_projects/notion_BHtrans_project/mock_audio/3407431768028.mp3", "rb") as audio_file:
#         audio = audio_file.read()
#         text = await transcribe_audio(audio)
#         print(text)

# # Тестовая функция для создания ответа
# async def create_response_test():
#     text = "Hello, how are you?"
#     answer = await create_response(text)
#     print(answer)








