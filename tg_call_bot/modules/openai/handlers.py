from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

import logging
import os
import tempfile

from share.usecases import transcribe_file
from share.promt_utils import get_promt_call_analyze, get_promt_call_summary
from .state import AudioStates
from .client import create_gptAnswer

logger = logging.getLogger(__name__)
router = Router()

# --- Общие функции ---

async def _get_file_info(message: Message) -> tuple[str, str]:
    """Извлекает file_id и filename из сообщения с аудио"""
    if message.voice:
        return message.voice.file_id, "voice.ogg"
    elif message.audio:
        return message.audio.file_id, message.audio.file_name or "audio.mp3"
    else:  # document
        return message.document.file_id, message.document.file_name or "audio.mp3"

async def _process_audio_file(
    message: Message,
    processing_message: Message,
    system_prompt: str,
    output_filename: str,
    success_caption: str,
    header_text: str
) -> None:
    """Общая функция для обработки аудиофайлов"""
    try:
        file_id, filename = await _get_file_info(message)
        
        result = await transcribe_file(
            message.bot,
            file_id,
            filename,
            system_prompt
        )

        # Создаем временный файл с результатом
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(f"{header_text}\n")
            temp_file.write(f"Файл: {filename}\n")
            temp_file.write("=" * 50 + "\n\n")
            temp_file.write(result)
            temp_file_path = temp_file.name
        
        try:
            # Отправляем файл пользователю
            document = FSInputFile(temp_file_path, filename=output_filename)
            await message.answer_document(
                document=document,
                caption=success_caption
            )
            await processing_message.delete()
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке аудио: {e}")
        await processing_message.edit_text("❌ Произошла ошибка при обработке аудио")


@router.message(Command("transcribe"))
async def cmd_transcribe(message: Message, state: FSMContext):
    """Команда для транскрибации аудио по спикерам"""
    await message.answer(
        "🎙️ Отправьте аудиофайл для транскрибации по спикерам.\n"
        "Поддерживаются форматы: mp3, wav, ogg, m4a"
    )
    await state.set_state(AudioStates.waiting_for_audio_transcribe)

@router.message(Command("call_summary"))  
async def cmd_call_summary(message: Message, state: FSMContext):
    """Команда для создания профиля водителя из звонка"""
    await message.answer(
        "👤 Отправьте аудиозапись звонка для создания профиля водителя.\n"
        "Поддерживаются форматы: mp3, wav, ogg, m4a"
    )
    await state.set_state(AudioStates.waiting_for_audio_summary)

@router.message(Command("call_analysis"))
async def cmd_call_analysis(message: Message, state: FSMContext):
    """Команда для детального анализа звонка"""
    await message.answer(
        "📞 Отправьте аудиозапись звонка для анализа и создания резюме.\n"
        "Поддерживаются форматы: mp3, wav, ogg, m4a"
    )
    await state.set_state(AudioStates.waiting_for_audio_analysis)

# --- Обработка аудио для транскрибации ---

@router.message(AudioStates.waiting_for_audio_transcribe)
async def handle_transcribe_audio(message: Message, state: FSMContext):
    """Обработка аудио для транскрибации"""
    if not (message.voice or message.audio or message.document):
        await message.answer("❌ Пожалуйста, отправьте аудиофайл")
        return
    
    logger.info(f"Обработка аудио для транскрибации")
    
    processing = await message.answer("🎙️ Транскрибирую аудио...")
    
    try:
        # Промпт для транскрибации по спикерам
        system_prompt = """Транскрибируй этот аудиофайл и раздели речь по спикерам. 
        Формат ответа:
        
        Спикер 1: [текст]
        Спикер 2: [текст]
        
        """
        
        await _process_audio_file(
            message,
            processing,
            system_prompt,
            "transcription.txt",
            "✅ Транскрипция готова! Результат в файле.",
            "🎙️ Транскрипция аудиофайла"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при транскрибации: {e}")
        await processing.edit_text("❌ Произошла ошибка при обработке аудио")
    
    await state.clear()

@router.message(AudioStates.waiting_for_audio_summary)
async def handle_summary_audio(message: Message, state: FSMContext):
    """Обработка аудио для создания профиля водителя (суммаризация)"""
    if not (message.voice or message.audio or message.document):
        await message.answer("❌ Пожалуйста, отправьте аудиофайл")
        return
    
    processing = await message.answer("👤 Создаю профиль водителя...")
    
    try:
        # Используем промпт для суммаризации звонков
        system_prompt = get_promt_call_summary()
        
        await _process_audio_file(
            message,
            processing,
            system_prompt,
            "driver_profile.txt",
            "✅ Профиль водителя готов! Результат в файле.",
            "👤 Профиль водителя"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании профиля водителя: {e}")
        await processing.edit_text("❌ Произошла ошибка при обработке аудио")
    
    await state.clear()

@router.message(AudioStates.waiting_for_audio_analysis)
async def handle_analysis_audio(message: Message, state: FSMContext):
    """Обработка аудио для детального анализа звонка"""
    if not (message.voice or message.audio or message.document):
        await message.answer("❌ Пожалуйста, отправьте аудиофайл")
        return
    
    processing = await message.answer("📞 Анализирую звонок...")
    
    try:
        # Используем промпт для анализа звонков
        system_prompt = get_promt_call_analyze()
        
        await _process_audio_file(
            message,
            processing,
            system_prompt,
            "call_analysis.txt",
            "✅ Анализ звонка готов! Результат в файле.",
            "📞 Анализ звонка"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при анализе звонка: {e}")
        await processing.edit_text("❌ Произошла ошибка при обработке аудио")
    
    await state.clear()
