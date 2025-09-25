import os
import time
import glob
import logging

# Импортируем функции для управления пользователями из нового модуля
from share.user_manager import (
    is_allowed_user, add_allowed_user, remove_allowed_user, 
    get_allowed_users_list, reload_users, get_users_count
)

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


# Все функции управления пользователями теперь импортируются из user_manager
# Они остаются доступными в этом модуле для обратной совместимости