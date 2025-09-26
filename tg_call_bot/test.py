from modules.openai.client import transcription, create_gptAnswer
import asyncio


async def main():
    text = await transcription("./audio/t.m4a")
    print(text)
    answer = await create_gptAnswer(text, """
                                    Транскрибируй этот аудиофайл и раздели речь по спикерам. 
        Формат ответа:
        
        Спикер 1: [текст]
        Спикер 2: [текст]
        """)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())