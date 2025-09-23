from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile
from share.config import ADMINS
from share.utils import is_allowed_user

async def cmd_start(message: Message):
    # Проверка доступа уже выполняется в middleware, поэтому здесь пользователь авторизован
    await message.answer_photo(
        photo=FSInputFile("assets/logo.png"),
        caption="✅ Добро пожаловать! Я ваш бот для анализации звонков!\n"
        "Используйте /help для получения списка команд."
    )


# Обработчик команды /help
async def cmd_help(message: Message):
    help_text = """
🤖 Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/drivers - Показать список водителей
/call_summary - Суммаризация звонка
/transcribe - Транскрибация аудио по спикерам (работает коректно с двумя спикерами)
"""
    
    # Добавляем админские команды для администраторов
    if message.from_user.id in ADMINS:
        help_text += "\n🔧 <b>Команды администратора:</b>\n"
        help_text += "/admin - Панель администратора\n"
    
    help_text += "\nПо всем вопросам обращайтесь к разработчику @dohaAdam1"
    
    await message.answer(help_text)



def register_handlers(dp: Dispatcher):
    
    # Регистрация команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    