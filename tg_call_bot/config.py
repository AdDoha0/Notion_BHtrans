import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в переменных окружения")

# Настройки OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Не установлен OPENAI_API_KEY в переменных окружения")


NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    raise ValueError("Не установлен NOTION_KEY в переменных окружения")

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
if not NOTION_DATABASE_ID:
    raise ValueError("Не установлен NOTION_DATABASE_ID в переменных окружения")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Настройки администраторов (список ID администраторов)
ADMIN_IDS = [
    int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") 
    if admin_id.strip()
]

# Настройки базы данных (если понадобится)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")

# Настройки Redis (для хранения состояний FSM)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Настройки вебхука (если используется)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Настройки прокси (если нужен)
PROXY_URL = os.getenv("PROXY_URL")