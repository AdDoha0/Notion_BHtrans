import os
import time
import glob
import logging

from share.config import ALLOWED_USERS

logger = logging.getLogger(__name__)



def cleanup_temp_files(temp_dir: str, max_age_minutes: int = 60):
    """Очищает старые временные файлы"""
    try:
        if not os.path.exists(temp_dir):
            return
        
        current_time = time.time()
        files_removed = 0
        
        for file_path in glob.glob(os.path.join(temp_dir, "*")):
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_minutes * 60:  # конвертируем в секунды
                    os.remove(file_path)
                    files_removed += 1
                    logger.info(f"Удален старый временный файл: {file_path}")
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {file_path}: {e}")
        
        if files_removed > 0:
            logger.info(f"Очищено {files_removed} старых временных файлов")
            
    except Exception as e:
        logger.error(f"Ошибка при очистке временных файлов: {e}")


def is_allowed_user(user_id: int) -> bool:
    """Проверяет, разрешен ли доступ для пользователя"""
    return user_id in ALLOWED_USERS


def add_allowed_user(user_id: int) -> bool:
    """Добавляет пользователя в список разрешённых (только в рантайме)"""
    if user_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(user_id)
        logger.info(f"Пользователь {user_id} добавлен в список разрешённых")
        return True
    return False


def remove_allowed_user(user_id: int) -> bool:
    """Удаляет пользователя из списка разрешённых (только в рантайме)"""
    if user_id in ALLOWED_USERS:
        ALLOWED_USERS.remove(user_id)
        logger.info(f"Пользователь {user_id} удалён из списка разрешённых")
        return True
    return False


def get_allowed_users_list() -> list:
    """Возвращает список разрешённых пользователей"""
    return ALLOWED_USERS.copy()