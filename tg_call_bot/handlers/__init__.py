from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Пример FSM для обработки состояний
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()


# Обработчик команды /start
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я ваш Telegram бот. 👋\n"
        "Используйте /help для получения списка команд."
    )


# Обработчик команды /help
async def cmd_help(message: Message):
    help_text = """
🤖 Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/profile - Начать заполнение профиля
/cancel - Отменить текущее действие

Для получения дополнительной информации обратитесь к администратору.
    """
    await message.answer(help_text)


# Обработчик команды /profile
async def cmd_profile(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_name)
    await message.answer("Как вас зовут?")


# Обработчик отмены
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.clear()
    await message.answer("Действие отменено.")


# Обработчик текстовых сообщений в состоянии ожидания имени
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserStates.waiting_for_age)
    await message.answer("Сколько вам лет?")


# Обработчик текстовых сообщений в состоянии ожидания возраста
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.answer("Пожалуйста, введите корректный возраст (0-150).")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        return
    
    user_data = await state.get_data()
    name = user_data.get("name", "Неизвестно")
    
    await state.clear()
    await message.answer(
        f"Спасибо! Ваш профиль:\n"
        f"Имя: {name}\n"
        f"Возраст: {age}"
    )


# Обработчик всех остальных сообщений
async def echo_message(message: Message):
    await message.answer(
        f"Вы написали: {message.text}\n"
        "Используйте /help для получения списка команд."
    )


def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    
    # Регистрация команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_cancel, Command("cancel"))
    
    # Регистрация обработчиков состояний
    dp.message.register(process_name, UserStates.waiting_for_name)
    dp.message.register(process_age, UserStates.waiting_for_age)
    
    # Регистрация обработчика всех остальных сообщений (должен быть последним)
    dp.message.register(echo_message) 