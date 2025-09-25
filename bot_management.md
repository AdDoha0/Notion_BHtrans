# 🤖 Управление Telegram ботом

## ✅ Бот настроен для автоматического перезапуска!

Система автоматически:
- ✅ Запускает бота при загрузке сервера
- ✅ Перезапускает если бот упал  
- ✅ Перезапускает если бот завис (через 10 секунд)
- ✅ Ведет логи всех событий

## 📊 Основные команды

```bash
# Статус бота (работает/упал/сколько раз перезапускался)
sudo systemctl status telegram-bot

# Перезапуск бота (например, после обновления кода)
sudo systemctl restart telegram-bot

# Остановка бота
sudo systemctl stop telegram-bot

# Запуск бота (если был остановлен)
sudo systemctl start telegram-bot

# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Последние 50 строк логов
sudo journalctl -u telegram-bot -n 50
```

## 🔄 После обновления кода

Когда меняешь код в `tg_call_bot/`:

```bash
sudo systemctl restart telegram-bot
```

## 📋 Файлы логов

- **Системные логи**: `sudo journalctl -u telegram-bot`
- **Логи приложения**: `tg_call_bot/bot.log`

## 🚨 Если что-то пошло не так

```bash
# Проверить статус
sudo systemctl status telegram-bot

# Посмотреть последние ошибки
sudo journalctl -u telegram-bot -n 20

# Полностью перезагрузить сервис
sudo systemctl daemon-reload
sudo systemctl restart telegram-bot
```

## ⚙️ Настройки автоперезапуска

Настройки в `/etc/systemd/system/telegram-bot.service`:
- `Restart=always` - всегда перезапускать при падении
- `RestartSec=10` - ждать 10 секунд перед перезапуском
- `StartLimitIntervalSec=0` - без лимита попыток перезапуска 