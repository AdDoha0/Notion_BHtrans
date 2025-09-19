from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from share.usecases import transcribe_file
from share.promt_utils import get_promt_call_analyze
import logging

logger = logging.getLogger(__name__)
router = Router()

class AudioStates(StatesGroup):
    waiting_for_audio_transcribe = State()
    waiting_for_audio_summary = State()

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
    """Команда для суммаризации звонка"""
    await message.answer(
        "📞 Отправьте аудиозапись звонка для анализа и создания резюме.\n"
        "Поддерживаются форматы: mp3, wav, ogg, m4a"
    )
    await state.set_state(AudioStates.waiting_for_audio_summary)

@router.message(AudioStates.waiting_for_audio_transcribe)
async def handle_transcribe_audio(message: Message, state: FSMContext):
    """Обработка аудио для транскрибации"""
    if not (message.voice or message.audio or message.document):
        await message.answer("❌ Пожалуйста, отправьте аудиофайл")
        return
    
    processing = await message.answer("🎙️ Транскрибирую аудио...")
    
    try:
        # Определяем file_id и имя файла
        if message.voice:
            file_id = message.voice.file_id
            filename = "voice.ogg"
        elif message.audio:
            file_id = message.audio.file_id  
            filename = message.audio.file_name or "audio.mp3"
        else:  # document
            file_id = message.document.file_id
            filename = message.document.file_name or "audio.mp3"
        
        # Промпт для транскрибации по спикерам
        system_prompt = """Транскрибируй этот аудиофайл и раздели речь по спикерам. 
        Формат ответа:
        
        Спикер 1: [текст]
        Спикер 2: [текст]
        
        Если не можешь определить спикеров, просто верни полную транскрипцию."""
        
        result = await process_audio(
            message.bot, 
            file_id, 
            filename, 
            system_prompt,
            model="gpt-4o",
            max_tokens=3000
        )
        
        await processing.edit_text(f"✅ Транскрипция готова:\n\n{result}")
        
    except Exception as e:
        logger.error(f"Ошибка при транскрибации: {e}")
        await processing.edit_text("❌ Произошла ошибка при обработке аудио")
    
    await state.clear()

@router.message(AudioStates.waiting_for_audio_summary)
async def handle_summary_audio(message: Message, state: FSMContext):
    """Обработка аудио для суммаризации звонка"""
    if not (message.voice or message.audio or message.document):
        await message.answer("❌ Пожалуйста, отправьте аудиофайл")
        return
    
    processing = await message.answer("📞 Анализирую звонок...")
    
    try:
        # Определяем file_id и имя файла
        if message.voice:
            file_id = message.voice.file_id
            filename = "voice.ogg"
        elif message.audio:
            file_id = message.audio.file_id
            filename = message.audio.file_name or "audio.mp3"
        else:  # document
            file_id = message.document.file_id
            filename = message.document.file_name or "audio.mp3"
        
        # Используем промпт для анализа звонков
        system_prompt = get_promt_call_analyze()
        
        result = await transcribe_file(
            message.bot,
            file_id, 
            filename,
            system_prompt
        )
        
        await processing.edit_text(f"✅ Анализ звонка готов:\n\n{result}")
        
    except Exception as e:
        logger.error(f"Ошибка при анализе звонка: {e}")
        await processing.edit_text("❌ Произошла ошибка при обработке аудио")
    
    await state.clear()
