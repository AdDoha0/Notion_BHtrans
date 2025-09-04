import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, LOG_LEVEL, WEBHOOK_URL, WEBHOOK_PATH
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация обработчиков
    register_handlers(dp)
    
    # Запуск бота
    if WEBHOOK_URL:
        # Запуск через вебхук
        app = web.Application()
        
        # Настройка вебхука
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_handler.register(app, path=WEBHOOK_PATH)
        
        # Установка вебхука
        await bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_PATH}")
        
        # Запуск веб-сервера
        web.run_app(app, host="0.0.0.0", port=8000)
    else:
        # Запуск через long polling
        logger.info("Запуск бота через long polling...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")



