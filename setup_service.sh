#!/bin/bash

echo "🚀 Настройка автоматического перезапуска Telegram бота..."

# Проверяем, что мы в правильной директории
if [ ! -f "telegram-bot.service" ]; then
    echo "❌ Файл telegram-bot.service не найден!"
    exit 1
fi

if [ ! -f "tg_call_bot/main.py" ]; then
    echo "❌ Файл tg_call_bot/main.py не найден!"
    exit 1
fi

echo "📋 Копируем service файл в systemd..."
sudo cp telegram-bot.service /etc/systemd/system/

echo "🔄 Перезагружаем systemd daemon..."
sudo systemctl daemon-reload

echo "✅ Включаем автозапуск сервиса..."
sudo systemctl enable telegram-bot

echo "🎯 Запускаем сервис..."
sudo systemctl start telegram-bot

echo ""
echo "✅ Готово! Бот настроен для автоматического перезапуска."
echo ""
echo "📊 Полезные команды:"
echo "  sudo systemctl status telegram-bot    # статус бота"
echo "  sudo systemctl restart telegram-bot   # перезапуск бота"
echo "  sudo systemctl stop telegram-bot      # остановка бота"
echo "  sudo journalctl -u telegram-bot -f    # логи в реальном времени"
echo ""
echo "🔍 Проверяем статус:"
sudo systemctl status telegram-bot --no-pager 