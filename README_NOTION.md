# BH Trans Bot - Notion Integration

Telegram бот для работы с базой данных водителей в Notion.

## 🎯 Текущий функционал

- ✅ Просмотр списка водителей из Notion
- ✅ Добавление текстовых комментариев к водителям
- ✅ Просмотр детальной информации о водителях
- ✅ Просмотр истории комментариев
- ❌ Поддержка голосовых сообщений (удалена)

## 📋 Доступные команды

- `/start` - начать работу с ботом
- `/drivers` - выбрать водителя и добавить комментарий
- `/driver_info` - просмотр информации о водителях
- `/help` - показать справку

## 🛠️ Настройка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` по образцу `env_example.txt`:
```
BOT_TOKEN=your_bot_token_here
NOTION_KEY=your_notion_integration_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

3. Запустите бота:
```bash
python main.py
```

## 📁 Структура проекта

```
tg_call_bot/
├── main.py                 # Точка входа
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости
├── handlers/
│   ├── cmd.py            # Регистрация обработчиков
│   ├── handlers.py       # Общие обработчики (пустой)
│   └── notion_handlers.py # Обработчики Notion
└── services/
    └── notion.py         # Работа с Notion API
```

## 🔄 Последние изменения

Из проекта была полностью удалена функциональность ИИ:
- Удален сервис `ai.py`
- Убрана поддержка голосовых сообщений
- Удалена зависимость от OpenAI
- Бот теперь работает только с текстовыми комментариями

Подробности в [CHANGELOG.md](../CHANGELOG.md). 