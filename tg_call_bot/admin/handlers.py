from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import psutil
import os
from datetime import datetime

from config import ADMINS

logger = logging.getLogger(__name__)

router = Router()

# Состояния для админ панели
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

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
            # InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="📋 Логи", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")
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
    
    action = callback.data.split("_")[1]
    
    if action == "stats":
        await show_stats(callback)
    elif action == "system":
        await show_system_info(callback)
    elif action == "broadcast":
        await start_broadcast(callback, state)
    elif action == "logs":
        await show_logs(callback)
    elif action == "close":
        await callback.message.delete()
    elif action == "back":
        await show_main_menu(callback)

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

