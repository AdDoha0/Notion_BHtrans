"""
Обработчики для работы с Notion в Telegram боте
"""

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from services.notion import get_driver_list, add_comment, get_driver_info, get_driver_comments

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

# Состояния для FSM
class NotionStates(StatesGroup):
    waiting_for_driver_selection = State()
    waiting_for_comment = State()

@router.message(Command("start"))
async def start_command(message: Message):
    """Обрабатывает команду /start"""
    welcome_text = """
👋 **Добро пожаловать в BH Trans Bot!**

Этот бот поможет вам работать с базой данных водителей в Notion.

🚀 **Быстрый старт:**
• `/drivers` - добавить комментарий к водителю
• `/driver_info` - просмотр информации о водителях  
• `/help` - подробная справка

💡 **Подсказка:** Отправляйте текстовые комментарии для добавления заметок к водителям!
    """
    
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("help"))
async def show_help(message: Message):
    """Показывает справку по командам"""
    help_text = """
🤖 **Помощь по боту**

📋 **Доступные команды:**
• `/start` - начать работу с ботом
• `/drivers` - выбрать водителя и добавить комментарий
• `/driver_info` - просмотр информации о водителях
• `/help` - показать эту справку

💬 **Как добавить комментарий:**
1. Выберите команду `/drivers`
2. Выберите водителя из списка  
3. Отправьте текстовый комментарий

✨ **Особенности:**
• Комментарии сохраняются как отдельные записи в Notion
• Просмотр истории комментариев
• Разделение между статическими заметками и динамическими комментариями

❓ Если у вас есть вопросы, обратитесь к администратору.
    """
    
    await message.answer(help_text, parse_mode="Markdown")

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
        
        info_text += "\n💬 Теперь отправьте запись звонка:"
        
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
    """Обрабатывает ввод комментария (текст или голос)"""
    
    try:
        # Получаем данные из состояния
        state_data = await state.get_data()
        driver_id = state_data.get('selected_driver_id')
        driver_name = state_data.get('selected_driver_name')
        
        if not driver_id:
            await message.answer("❌ Ошибка: не найден выбранный водитель")
            await state.clear()
            return
        
        # Обрабатываем только текстовые сообщения
        if message.text:
            comment_text = message.text.strip()
            processing_msg = await message.answer("🔄 Добавляю комментарий...")
        
        else:
            await message.answer("❌ Отправьте текстовый комментарий:")
            return
        
        if not comment_text or comment_text.strip() == "":
            await message.answer("❌ Комментарий не может быть пустым. Попробуйте еще раз:")
            return
        
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
        
        # Добавляем заметки (статичные)
        if driver_info['notes']:
            info_text += f"\n📝 **Заметки:**\n{driver_info['notes']}\n"
        else:
            info_text += f"\n📝 Заметки отсутствуют\n"
        
        # Получаем и добавляем комментарии
        comments = await get_driver_comments(driver_id)
        if comments:
            info_text += f"\n💬 **Комментарии ({len(comments)}):**\n"
            # Показываем последние 3 комментария
            for i, comment in enumerate(comments[-3:]):
                created_time = comment.get('created_time', '')
                if created_time:
                    # Форматируем время
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_time = created_time[:10]  # Берем только дату
                else:
                    formatted_time = "Неизвестно"
                
                comment_text = comment.get('text', '')[:100] + "..." if len(comment.get('text', '')) > 100 else comment.get('text', '')
                info_text += f"• [{formatted_time}] {comment_text}\n"
            
            if len(comments) > 3:
                info_text += f"... и еще {len(comments) - 3} комментариев\n"
        else:
            info_text += f"\n💬 Комментарии отсутствуют\n"
        
        # Кнопки для работы с комментариями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
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

@router.callback_query(F.data.startswith("show_comments:"))
async def show_all_comments(callback: CallbackQuery):
    """Показывает все комментарии к водителю"""
    
    try:
        driver_id = callback.data.split(":", 1)[1]
        
        # Получаем информацию о водителе и его комментарии
        driver_info = await get_driver_info(driver_id)
        comments = await get_driver_comments(driver_id)
        
        if not driver_info:
            await callback.answer("❌ Не удалось получить информацию о водителе")
            return
        
        # Формируем текст с комментариями
        info_text = f"💬 **Все комментарии к {driver_info['name']}**\n\n"
        
        if comments:
            info_text += f"Всего комментариев: {len(comments)}\n\n"
            
            for i, comment in enumerate(comments, 1):
                created_time = comment.get('created_time', '')
                if created_time:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_time = created_time[:10]
                else:
                    formatted_time = "Неизвестно"
                
                comment_text = comment.get('text', '')
                info_text += f"**{i}.** [{formatted_time}]\n{comment_text}\n\n"
        else:
            info_text += "Комментарии отсутствуют"
        
        # Кнопки навигации
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙 К информации о водителе", 
                callback_data=f"info_show:{driver_id}"
            )],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="info_cancel")]
        ])
        
        await callback.message.edit_text(
            info_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе комментариев: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке комментариев")

@router.callback_query(F.data == "back_to_drivers")
async def back_to_drivers_list(callback: CallbackQuery):
    """Возврат к списку водителей"""
    # Эмулируем команду /driver_info
    fake_message = type('obj', (object,), {
        'answer': callback.message.edit_text,
        'from_user': callback.from_user
    })()
    
    await show_driver_info_command(fake_message) 