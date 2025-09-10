"""
Обработчики для работы с Notion в Telegram боте
"""

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from services.notion import get_driver_list, add_comment, get_driver_info

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

# Состояния для FSM
class NotionStates(StatesGroup):
    waiting_for_driver_selection = State()
    waiting_for_comment = State()

@router.message(Command("drivers"))
async def show_drivers_command(message: Message, state: FSMContext):
    """Показывает список водителей для выбора"""
    
    try:
        await message.answer("🔄 Загружаю список водителей...")
        
        # Получаем список водителей
        drivers = await get_driver_list()
        
        if not drivers:
            await message.answer("❌ Водители не найдены в базе данных")
            return
        
        # Создаем inline клавиатуру с водителями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for driver in drivers:
            # Ограничиваем длину имени для кнопки
            display_name = driver['name'][:30] + "..." if len(driver['name']) > 30 else driver['name']
            
            button = InlineKeyboardButton(
                text=display_name,
                callback_data=f"driver_select:{driver['id']}"
            )
            keyboard.inline_keyboard.append([button])
        
        # Добавляем кнопку отмены
        cancel_button = InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="driver_cancel"
        )
        keyboard.inline_keyboard.append([cancel_button])
        
        await message.answer(
            f"👥 Найдено {len(drivers)} водителей.\nВыберите водителя для добавления комментария:",
            reply_markup=keyboard
        )
        
        # Устанавливаем состояние ожидания выбора водителя
        await state.set_state(NotionStates.waiting_for_driver_selection)
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка водителей: {e}")
        await message.answer("❌ Произошла ошибка при загрузке списка водителей")

@router.callback_query(F.data.startswith("driver_select:"))
async def handle_driver_selection(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор водителя"""
    
    try:
        # Извлекаем ID водителя из callback_data
        driver_id = callback.data.split(":", 1)[1]
        
        # Получаем информацию о водителе
        driver_info = await get_driver_info(driver_id)
        
        if not driver_info:
            await callback.answer("❌ Не удалось получить информацию о водителе")
            return
        
        # Сохраняем информацию о выбранном водителе в состояние
        await state.update_data(
            selected_driver_id=driver_id,
            selected_driver_name=driver_info['name']
        )
        
        # Показываем информацию о водителе
        info_text = f"👤 Выбран водитель: **{driver_info['name']}**\n\n"
        
        if driver_info['status']:
            info_text += f"📊 Статус: {driver_info['status']}\n"
        
        if driver_info['number']:
            info_text += f"📞 Номер: {driver_info['number']}\n"
        
        if driver_info['about_driver']:
            info_text += f"ℹ️ О водителе: {driver_info['about_driver'][:100]}...\n" if len(driver_info['about_driver']) > 100 else f"ℹ️ О водителе: {driver_info['about_driver']}\n"
        
        if driver_info['date']:
            info_text += f"📅 Дата: {driver_info['date']}\n"
        
        if driver_info['trailer']:
            info_text += f"🚛 Прицеп: Да\n"
        
        if driver_info['notes']:
            notes_preview = driver_info['notes'][:200] + "..." if len(driver_info['notes']) > 200 else driver_info['notes']
            info_text += f"\n📝 Текущие заметки:\n{notes_preview}\n"
        
        info_text += "\n💬 Теперь отправьте комментарий, который хотите добавить:"
        
        # Создаем клавиатуру с кнопкой отмены
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="comment_cancel")]
        ])
        
        await callback.message.edit_text(
            info_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        # Устанавливаем состояние ожидания комментария
        await state.set_state(NotionStates.waiting_for_comment)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при выборе водителя: {e}")
        await callback.answer("❌ Произошла ошибка при выборе водителя")

@router.callback_query(F.data == "driver_cancel")
async def handle_driver_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена выбора водителя"""
    await callback.message.edit_text("❌ Выбор водителя отменен")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "comment_cancel")
async def handle_comment_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления комментария"""
    await callback.message.edit_text("❌ Добавление комментария отменено")
    await state.clear()
    await callback.answer()

@router.message(StateFilter(NotionStates.waiting_for_comment))
async def handle_comment_input(message: Message, state: FSMContext):
    """Обрабатывает ввод комментария"""
    
    try:
        # Получаем данные из состояния
        state_data = await state.get_data()
        driver_id = state_data.get('selected_driver_id')
        driver_name = state_data.get('selected_driver_name')
        
        if not driver_id:
            await message.answer("❌ Ошибка: не найден выбранный водитель")
            await state.clear()
            return
        
        comment_text = message.text.strip()
        
        if not comment_text:
            await message.answer("❌ Комментарий не может быть пустым. Попробуйте еще раз:")
            return
        
        # Показываем сообщение о процессе добавления
        processing_msg = await message.answer("🔄 Добавляю комментарий...")
        
        # Добавляем комментарий
        success = await add_comment(driver_id, comment_text)
        
        if success:
            await processing_msg.edit_text(
                f"✅ Комментарий успешно добавлен!\n\n"
                f"👤 Водитель: {driver_name}\n"
                f"💬 Комментарий: {comment_text}"
            )
        else:
            await processing_msg.edit_text("❌ Не удалось добавить комментарий. Попробуйте позже.")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении комментария: {e}")
        await message.answer("❌ Произошла ошибка при добавлении комментария")
        await state.clear()

@router.message(Command("driver_info"))
async def show_driver_info_command(message: Message):
    """Показывает список водителей для просмотра информации"""
    
    try:
        await message.answer("🔄 Загружаю список водителей...")
        
        drivers = await get_driver_list()
        
        if not drivers:
            await message.answer("❌ Водители не найдены в базе данных")
            return
        
        # Создаем inline клавиатуру для просмотра информации
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for driver in drivers:
            display_name = driver['name'][:30] + "..." if len(driver['name']) > 30 else driver['name']
            
            button = InlineKeyboardButton(
                text=display_name,
                callback_data=f"info_show:{driver['id']}"
            )
            keyboard.inline_keyboard.append([button])
        
        cancel_button = InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="info_cancel"
        )
        keyboard.inline_keyboard.append([cancel_button])
        
        await message.answer(
            f"👥 Найдено {len(drivers)} водителей.\nВыберите водителя для просмотра информации:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка водителей: {e}")
        await message.answer("❌ Произошла ошибка при загрузке списка водителей")

@router.callback_query(F.data.startswith("info_show:"))
async def show_detailed_driver_info(callback: CallbackQuery):
    """Показывает детальную информацию о водителе"""
    
    try:
        driver_id = callback.data.split(":", 1)[1]
        
        driver_info = await get_driver_info(driver_id)
        
        if not driver_info:
            await callback.answer("❌ Не удалось получить информацию о водителе")
            return
        
        # Формируем детальную информацию
        info_text = f"👤 **{driver_info['name']}**\n\n"
        
        info_text += f"🆔 ID: `{driver_info['id'][:8]}...`\n"
        
        if driver_info['status']:
            info_text += f"📊 Статус: {driver_info['status']}\n"
        
        if driver_info['about_driver']:
            info_text += f"ℹ️ О водителе: {driver_info['about_driver']}\n"
        
        if driver_info['number']:
            info_text += f"📞 Номер: {driver_info['number']}\n"
        
        if driver_info['date']:
            info_text += f"📅 Дата: {driver_info['date']}\n"
        
        info_text += f"🚛 Прицеп: {'Да' if driver_info['trailer'] else 'Нет'}\n"
        
        if driver_info['notes']:
            info_text += f"\n📝 **Заметки:**\n{driver_info['notes']}\n"
        else:
            info_text += f"\n📝 Заметки отсутствуют\n"
        
        # Кнопка для добавления комментария
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💬 Добавить комментарий", 
                callback_data=f"driver_select:{driver_id}"
            )],
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_drivers")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="info_cancel")]
        ])
        
        await callback.message.edit_text(
            info_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации о водителе: {e}")
        await callback.answer("❌ Произошла ошибка при получении информации")

@router.callback_query(F.data == "info_cancel")
async def handle_info_cancel(callback: CallbackQuery):
    """Закрытие просмотра информации"""
    await callback.message.edit_text("ℹ️ Просмотр информации завершен")
    await callback.answer()

@router.callback_query(F.data == "back_to_drivers")
async def back_to_drivers_list(callback: CallbackQuery):
    """Возврат к списку водителей"""
    # Эмулируем команду /driver_info
    fake_message = type('obj', (object,), {
        'answer': callback.message.edit_text,
        'from_user': callback.from_user
    })()
    
    await show_driver_info_command(fake_message) 