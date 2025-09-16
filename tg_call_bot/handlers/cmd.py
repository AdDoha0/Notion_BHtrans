from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


async def cmd_start(message: Message):
    await message.answer(
        "Ассаламу алейкум! я ваш бот для анализации звонков\n"
        "Используйте /help для получения списка команд."
    )


# Обработчик команды /help
async def cmd_help(message: Message):
    help_text = """
🤖 Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/drivers - Показать список водителей

Для получения дополнительной информации обратитесь к администратору.
    """
    await message.answer(help_text)



def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    
    # Регистрация команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    