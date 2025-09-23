import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web
import aiohttp

from share.config import BOT_TOKEN, LOG_LEVEL, WEBHOOK_URL, WEBHOOK_PATH
from share.middleware import AccessControlMiddleware
from handlers.cmd import register_handlers
from modules.notion.handlers import router as notion_router
from modules.admin.handlers import router as admin_router
from modules.openai.handlers import router as openai_router


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация бота и диспетчера с новым синтаксисом
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=default)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем middleware для контроля доступа
    dp.message.middleware(AccessControlMiddleware())
    dp.callback_query.middleware(AccessControlMiddleware())
    
    # Подключаем админ обработчики (приоритет)
    dp.include_router(admin_router)
    # Подключаем обработчики Notion
    dp.include_router(notion_router)
    # Подключаем обработчики OpenAI
    dp.include_router(openai_router)
    
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
        try:
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logger.error(f"Ошибка при polling: {e}")
            await asyncio.sleep(5)  # Пауза перед повторной попыткой
            raise

 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")



