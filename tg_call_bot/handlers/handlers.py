from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging

from services.ai import create_response

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

@router.message(StateFilter("generating"))
async def wait_response(message: Message, state: FSMContext):
    await message.answer("Ожидайте! идет генерация ответа...")

@router.message()
async def handle_message(message: Message, state: FSMContext): 
    logger.info(f"Получено сообщение: {message.text}")
    await state.set_state("generating")
    
    try:
        answer = await create_response(message.text)
        await message.answer(answer)
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await message.answer("Произошла ошибка при обработке вашего сообщения")
    finally:
        await state.clear()