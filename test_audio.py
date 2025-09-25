

import asyncio
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'tg_call_bot'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tg_call_bot'))
# from modules.openai.client import process_audio_to_comment, transcription, create_gptAnswer

async def test_audio_processing():
    """Тест обработки аудио файла"""
    
    # Путь к тестовому аудио файлу
    audio_file = "mock_audio/test.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ Файл {audio_file} не найден")
        return
    
    try:
        print("🎙️ Тестирую транскрибацию...")
        transcribed = await transcription(audio_file)
        print(f"📝 Транскрибированный текст:\n{transcribed}\n")
        
        print("🤖 Тестирую анализ GPT...")
        analysis = await create_gptAnswer(transcribed, "Проанализируй этот текст и дай краткое резюме.")
        print(f"📊 Анализ GPT:\n{analysis}\n")
        
        print("✅ Полный процесс:")
        full_result = await process_audio_to_comment(audio_file)
        print(f"🎯 Итоговый результат:\n{full_result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def test_text_processing():
    """Тест обработки текста"""
    
    test_text = """
    Звонок с водителем Иваном Петровым.
    Водитель: Здравствуйте, я хочу узнать про работу в вашей компании.
    HR: Здравствуйте! Расскажите о своем опыте.
    Водитель: У меня 5 лет опыта, есть свой тягач Volvo, готов работать.
    HR: Отлично, какие у вас вопросы?
    Водитель: Меня интересует оплата и график работы.
    HR: Оплата от 200 тысяч в месяц, график свободный.
    Водитель: Звучит интересно, нужно подумать.
    """
    
    try:
        print("🤖 Тестирую анализ текста через GPT...")
        analysis = await create_gptAnswer(test_text, "Проанализируй этот разговор и создай профиль водителя.")
        print(f"📊 Анализ GPT:\n{analysis}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов...\n")
    
    # Тест обработки текста (не требует аудио файла)
    asyncio.run(test_text_processing())
    
    print("\n" + "="*50 + "\n")
    
    # Тест обработки аудио (требует файл)
    asyncio.run(test_audio_processing()) 