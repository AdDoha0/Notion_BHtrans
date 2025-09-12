from openai import AsyncOpenAI
from config import OPENAI_KEY
import asyncio

client = AsyncOpenAI(api_key=OPENAI_KEY)

def get_promt() -> str:
    with open("promt.txt", "r") as file:
        return file.read()

promt = get_promt()


async def transcription(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text


async def create_gptAnswer(message: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-5",
        reasoning_effort="high",
        messages=[
            {"role": "system", "content": promt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


transcription_text = asyncio.run(transcription("../mock_audio/hr_test_2.mp3"))
print(asyncio.run(create_gptAnswer(transcription_text)))
