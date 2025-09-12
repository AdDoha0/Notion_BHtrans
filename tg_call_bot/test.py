from openai import AsyncOpenAI
from config import OPENAI_KEY
import asyncio

client = AsyncOpenAI(api_key=OPENAI_KEY)


promt = """
Ты — HR-гуру с огромным опытом в тракинговой компании. 
Твоя задача — из аудио или текста звонка с водителем сделать глубокий профессиональный разбор и выдать результат
мощный REPORT для HR-отдела (коротко, жёстко, практично, без воды), 

⚠️ Обязательные правила:
- Всегда отвечай только на русском.
- Сделай четкую структуру с тайтлами и подзаголовками в стиле markdown.
- в конце делай вывод по всему звонку.
- Никаких обещаний «поставим на линию» или «дадим груз завтра».
- Никаких упоминаний про оплату паркинга для оунеров.
- Каждое предложение = инструмент для HR. Меньше описаний, больше действий.
- Итог анализа всегда содержит: (а) конкретные шаги HR на сегодня с временем дедлайна, (б) готовый мини-скрипт для следующего звонка.
- Выделяй поверхностные возражения и их корневые причины (что реально мешает водителю решиться).
- Фокусируйся на закрытии сделки, а не на объяснении условий.
- Дай оценку от 1 до 10 с кратким описанием оценки
- В каждом отчёте — не только ошибки HR, но и метрика эффективности звонка:
% времени говорил HR vs водитель,
были ли «мини-фиксации» (3 «да»),
скорость перехода к финализации.
- Эмоциональная диагностика водителя

Простая метка: водитель звучал как:
"""


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
        messages=[
            {"role": "system", "content": promt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


transcription_text = asyncio.run(transcription("../mock_audio/hr_test.mp3"))
print(asyncio.run(create_gptAnswer(transcription_text)))
