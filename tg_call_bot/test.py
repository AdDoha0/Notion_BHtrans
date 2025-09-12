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



