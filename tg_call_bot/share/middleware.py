from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import logging

from share.utils import is_allowed_user

logger = logging.getLogger(__name__)


class AccessControlMiddleware(BaseMiddleware):
    """Middleware для ограничения доступа к боту только разрешённым пользователям"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем только сообщения и callback query
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            
            if not is_allowed_user(user_id):
                # Логируем попытку доступа
                username = event.from_user.username or "неизвестно"
                logger.warning(f"Отклонён доступ для пользователя {user_id} (@{username})")
                
                # Отправляем сообщение об отказе в доступе
                if isinstance(event, Message):
                    await event.answer("⛔ У вас нет доступа к этому боту. Для получения доступа писать сюда -> @dohaAdam1")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⛔ У вас нет доступа к этому боту. Для получения доступа писать сюда -> @dohaAdam1", show_alert=True)
                
                return  # Прерываем выполнение
        
        # Если проверка пройдена или это не сообщение/callback - продолжаем
        return await handler(event, data) 