from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
import psutil
import os
from datetime import datetime

from share.config import ADMINS
from share.promt_utils import (
    get_main_prompt, get_response_template, save_main_prompt, save_response_template,
    get_summary_main_prompt, get_summary_template, save_summary_main_prompt, save_summary_template
)
from .states import AdminStates

logger = logging.getLogger(__name__)

router = Router()


# Проверка админских прав
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Главное меню админ панели
def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="💻 Система", callback_data="admin_system")
        ],
        [
            InlineKeyboardButton(text="🤖 Промт", callback_data="admin_prompt"),
            InlineKeyboardButton(text="📋 Логи", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")
        ]
    ])
    return keyboard

# Меню управления промтом
def get_prompt_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Анализ звонков", callback_data="admin_analyze_menu")
        ],
        [
            InlineKeyboardButton(text="👤 Профиль водителя", callback_data="admin_summary_menu")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")
        ]
    ])
    return keyboard

def get_analyze_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👁️ Текущий промт", callback_data="admin_prompt_view"),
            InlineKeyboardButton(text="👁️ Текущий шаблон", callback_data="admin_template_view")
        ],
        [
            InlineKeyboardButton(text="✏️ Изменить промт", callback_data="admin_prompt_main"),
            InlineKeyboardButton(text="✏️ Изменить шаблон", callback_data="admin_prompt_template")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_prompt")
        ]
    ])
    return keyboard

def get_summary_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👁️ Текущий промт", callback_data="admin_summary_prompt_view"),
            InlineKeyboardButton(text="👁️ Текущий шаблон", callback_data="admin_summary_template_view")
        ],
        [
            InlineKeyboardButton(text="✏️ Изменить промт", callback_data="admin_summary_prompt_main"),
            InlineKeyboardButton(text="✏️ Изменить шаблон", callback_data="admin_summary_prompt_template")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_prompt")
        ]
    ])
    return keyboard

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Главная команда админ панели"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к админ панели.")
        return
    
    text = f"""
🔧 <b>Админ панель</b>

Добро пожаловать, {message.from_user.first_name}!
Выберите нужное действие:
    """
    
    await message.answer(text, reply_markup=get_admin_keyboard())

@router.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопок админ панели"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    action = callback.data
    
    if action == "admin_stats":
        await show_stats(callback)
    elif action == "admin_system":
        await show_system_info(callback)
    elif action == "admin_broadcast":
        await start_broadcast(callback, state)
    elif action == "admin_logs":
        await show_logs(callback)
    elif action == "admin_prompt":
        await show_prompt_menu(callback)
    elif action == "admin_close":
        await callback.message.delete()
    elif action == "admin_back":
        await show_main_menu(callback)
    elif action == "admin_prompt_main":
        await edit_main_prompt(callback, state)
    elif action == "admin_prompt_template":
        await edit_response_template(callback, state)
    elif action == "admin_prompt_view":
        await view_current_prompt(callback)
    elif action == "admin_template_view":
        await view_current_template(callback)
    elif action == "admin_analyze_menu":
        await show_analyze_menu(callback)
    elif action == "admin_summary_menu":
        await show_summary_menu(callback)
    elif action == "admin_summary_prompt_view":
        await view_current_summary_prompt(callback)
    elif action == "admin_summary_template_view":
        await view_current_summary_template(callback)
    elif action == "admin_summary_prompt_main":
        await edit_summary_main_prompt(callback, state)
    elif action == "admin_summary_prompt_template":
        await edit_summary_response_template(callback, state)

async def show_stats(callback: CallbackQuery):
    """Показать статистику бота"""
    # Базовая статистика
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    
    text = f"""
📊 <b>Статистика бота</b>

⏰ Время работы системы: {uptime.days} дней, {uptime.seconds//3600} часов
👥 Админов в системе: {len(ADMINS)}
📈 Статус: Активен
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def show_system_info(callback: CallbackQuery):
    """Показать информацию о системе"""
    # Получаем информацию о системе
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    text = f"""
💻 <b>Информация о системе</b>

🖥️ CPU: {cpu_percent}%
🧠 RAM: {memory.percent}% ({memory.used//1024//1024} MB / {memory.total//1024//1024} MB)
💾 Диск: {disk.percent}% ({disk.used//1024//1024//1024} GB / {disk.total//1024//1024//1024} GB)
🐍 Python: {os.sys.version.split()[0]}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_system")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Начать процесс рассылки"""
    text = """
📢 <b>Рассылка сообщений</b>

Отправьте сообщение, которое нужно разослать всем пользователям.
Для отмены используйте /cancel
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    """Обработка сообщения для рассылки"""
    if not is_admin(message.from_user.id):
        return
    
    # Здесь можно добавить логику рассылки
    # Пока что просто подтверждаем получение
    await message.answer(f"✅ Сообщение для рассылки получено:\n\n{message.text}")
    await message.answer("ℹ️ Функция массовой рассылки будет реализована в следующих версиях.")
    
    await state.clear()

@router.message(Command("cancel"))
async def cancel_admin_action(message: Message, state: FSMContext):
    """Отмена текущего админского действия"""
    if not is_admin(message.from_user.id):
        return
    
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("❌ Действие отменено.")
    else:
        await message.answer("ℹ️ Нет активных действий для отмены.")

async def show_logs(callback: CallbackQuery):
    """Показать последние логи"""
    text = """
📋 <b>Системные логи</b>

🟢 Бот запущен успешно
🔄 Последняя активность: сейчас
📊 Обработано сообщений: активно

ℹ️ Детальные логи доступны в консоли сервера.
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню админ панели"""
    text = f"""
🔧 <b>Админ панель</b>

Добро пожаловать, {callback.from_user.first_name}!
Выберите нужное действие:
    """
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())

async def show_prompt_menu(callback: CallbackQuery):
    """Показать меню управления промтом"""
    text = """
🤖 <b>Управление промтом</b>

Выберите что вы хотите изменить:
• <b>Основной промт</b> - инструкции и правила для AI
• <b>Шаблон ответа</b> - структура отчета

Или посмотрите текущие настройки.
    """
    
    await callback.message.edit_text(text, reply_markup=get_prompt_keyboard())

async def edit_main_prompt(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование основного промта"""
    current_prompt = get_main_prompt()
    
    text = f"""
📝 <b>Редактирование основного промта</b>

<b>Текущий промт:</b>
<code>{current_prompt}</code>

Отправьте новый промт следующим сообщением.
Для отмены используйте /cancel
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_prompt")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_main_prompt)

async def edit_response_template(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование шаблона ответа"""
    current_template = get_response_template()
    
    text = f"""
📋 <b>Редактирование шаблона ответа</b>

<b>Текущий шаблон:</b>
<code>{current_template}</code>

Отправьте новый шаблон следующим сообщением.
Для отмены используйте /cancel
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_prompt")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_response_template)

async def view_current_prompt(callback: CallbackQuery):
    """Показать текущий основной промт"""
    current_prompt = get_main_prompt()
    
    text = f"""
📝 <b>Текущий основной промт</b>

<code>{current_prompt}</code>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="admin_prompt_main")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_prompt")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def view_current_template(callback: CallbackQuery):
    """Показать текущий шаблон ответа"""
    current_template = get_response_template()
    
    text = f"""
📋 <b>Текущий шаблон ответа</b>

<code>{current_template}</code>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="admin_prompt_template")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_prompt")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.message(AdminStates.waiting_for_main_prompt)
async def process_main_prompt(message: Message, state: FSMContext):
    """Обработка нового основного промта"""
    if not is_admin(message.from_user.id):
        return
    
    new_prompt = message.text.strip()
    
    if save_main_prompt(new_prompt):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К управлению промтом", callback_data="admin_prompt")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="admin_back")]
        ])
        await message.answer("✅ Основной промт успешно обновлен!", reply_markup=keyboard)
        logger.info(f"Админ {message.from_user.id} обновил основной промт")
    else:
        await message.answer("❌ Ошибка при сохранении промта. Попробуйте еще раз.")
        logger.error(f"Ошибка сохранения промта от админа {message.from_user.id}")
    
    await state.clear()

@router.message(AdminStates.waiting_for_response_template)
async def process_response_template(message: Message, state: FSMContext):
    """Обработка нового шаблона ответа"""
    if not is_admin(message.from_user.id):
        return
    
    new_template = message.text.strip()
    
    if save_response_template(new_template):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К управлению промтом", callback_data="admin_prompt")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="admin_back")]
        ])
        await message.answer("✅ Шаблон ответа успешно обновлен!", reply_markup=keyboard)
        logger.info(f"Админ {message.from_user.id} обновил шаблон ответа")
    else:
        await message.answer("❌ Ошибка при сохранении шаблона. Попробуйте еще раз.")
        logger.error(f"Ошибка сохранения шаблона от админа {message.from_user.id}")
    
    await state.clear()

# --- Функции для управления суммаризацией ---

async def show_analyze_menu(callback: CallbackQuery):
    """Показать меню управления промтами анализа звонков"""
    text = """
🔍 <b>Управление анализом звонков</b>

Настройка промптов для анализа звонков с водителями.
Выберите что вы хотите изменить или посмотреть.
"""
    await callback.message.edit_text(text, reply_markup=get_analyze_menu_keyboard())

async def show_summary_menu(callback: CallbackQuery):
    """Показать меню управления промтами суммаризации"""
    text = """
👤 <b>Управление профилем водителя</b>

Настройка промптов для создания профиля водителя из звонков.
Выберите что вы хотите изменить или посмотреть.
"""
    await callback.message.edit_text(text, reply_markup=get_summary_menu_keyboard())

async def view_current_summary_prompt(callback: CallbackQuery):
    """Показать текущий промт суммаризации"""
    current_prompt = get_summary_main_prompt()
    
    text = f"""
📝 <b>Текущий промт для профиля водителя</b>

<code>{current_prompt}</code>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="admin_summary_prompt_main")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_summary_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def view_current_summary_template(callback: CallbackQuery):
    """Показать текущий шаблон суммаризации"""
    current_template = get_summary_template()
    
    text = f"""
📋 <b>Текущий шаблон профиля водителя</b>

<code>{current_template}</code>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="admin_summary_prompt_template")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_summary_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def edit_summary_main_prompt(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование промта суммаризации"""
    current_prompt = get_summary_main_prompt()
    
    text = f"""
📝 <b>Редактирование промта профиля водителя</b>

<b>Текущий промт:</b>
<code>{current_prompt}</code>

Отправьте новый промт следующим сообщением.
Для отмены используйте /cancel
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_summary_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_summary_main_prompt)

async def edit_summary_response_template(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование шаблона суммаризации"""
    current_template = get_summary_template()
    
    text = f"""
📋 <b>Редактирование шаблона профиля водителя</b>

<b>Текущий шаблон:</b>
<code>{current_template}</code>

Отправьте новый шаблон следующим сообщением.
Для отмены используйте /cancel
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_summary_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_summary_template)

@router.message(AdminStates.waiting_for_summary_main_prompt)
async def process_summary_main_prompt(message: Message, state: FSMContext):
    """Обработка нового промта суммаризации"""
    if not is_admin(message.from_user.id):
        return
    
    new_prompt = message.text.strip()
    
    if save_summary_main_prompt(new_prompt):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К управлению промтами", callback_data="admin_summary_menu")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="admin_back")]
        ])
        await message.answer("✅ Промт профиля водителя успешно обновлен!", reply_markup=keyboard)
        logger.info(f"Админ {message.from_user.id} обновил промт суммаризации")
    else:
        await message.answer("❌ Ошибка при сохранении промта. Попробуйте еще раз.")
        logger.error(f"Ошибка сохранения промта суммаризации от админа {message.from_user.id}")
    
    await state.clear()

@router.message(AdminStates.waiting_for_summary_template)
async def process_summary_template(message: Message, state: FSMContext):
    """Обработка нового шаблона суммаризации"""
    if not is_admin(message.from_user.id):
        return
    
    new_template = message.text.strip()
    
    if save_summary_template(new_template):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К управлению промтами", callback_data="admin_summary_menu")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="admin_back")]
        ])
        await message.answer("✅ Шаблон профиля водителя успешно обновлен!", reply_markup=keyboard)
        logger.info(f"Админ {message.from_user.id} обновил шаблон суммаризации")
    else:
        await message.answer("❌ Ошибка при сохранении шаблона. Попробуйте еще раз.")
        logger.error(f"Ошибка сохранения шаблона суммаризации от админа {message.from_user.id}")
    
    await state.clear()

