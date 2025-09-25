import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


ALLOWED_USERS = [6979740321, 1922352366]

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в переменных окружения")

NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    raise ValueError("Не установлен NOTION_KEY в переменных окружения")

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
if not NOTION_DATABASE_ID:
    raise ValueError("Не установлен NOTION_DATABASE_ID в переменных окружения")

OPENAI_KEY = os.getenv("OPENAI_KEY")
if not OPENAI_KEY:
    raise ValueError("Не установлен OPENAI_KEY в переменных окружения")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Настройки администраторов
ADMINS_ENV = os.getenv("ADMINS", "")
if ADMINS_ENV:
    ADMINS = set(int(admin_id) for admin_id in ADMINS_ENV.split(","))
else:
    ADMINS = set()  # Пустой набор, если админы не заданы



# Настройки вебхука (если используется)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Настройки прокси (если нужен)
PROXY_URL = os.getenv("PROXY_URL")

# Ограничения для OpenAI API
MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "300"))  # Максимальный размер аудио в МБ