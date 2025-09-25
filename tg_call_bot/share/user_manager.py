import json
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class UserManager:
    """Класс для управления разрешенными пользователями с хранением в JSON файле"""
    
    def __init__(self, data_file_path: str = None):
        """
        Инициализация менеджера пользователей
        
        Args:
            data_file_path: Путь к JSON файлу с данными пользователей
        """
        if data_file_path is None:
            # Определяем путь к файлу относительно текущего файла
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(current_dir), 'data')
            self.data_file_path = os.path.join(data_dir, 'allowed_users.json')
        else:
            self.data_file_path = data_file_path
        
        # Создаем директорию data если её нет
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
        
        # Загружаем данные при инициализации
        self._allowed_users = self._load_users()
    
    def _load_users(self) -> List[int]:
        """Загружает список пользователей из JSON файла"""
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users = data.get('allowed_users', [])
                    logger.info(f"Загружено {len(users)} разрешенных пользователей из {self.data_file_path}")
                    return users
            else:
                # Если файл не существует, создаем его с пустым списком
                self._save_users([])
                logger.info(f"Создан новый файл пользователей: {self.data_file_path}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при загрузке пользователей из {self.data_file_path}: {e}")
            return []
    
    def _save_users(self, users: List[int]) -> bool:
        """Сохраняет список пользователей в JSON файл"""
        try:
            data = {"allowed_users": users}
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Список пользователей сохранен в {self.data_file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении пользователей в {self.data_file_path}: {e}")
            return False
    
    def is_allowed_user(self, user_id: int) -> bool:
        """Проверяет, разрешен ли доступ для пользователя"""
        return user_id in self._allowed_users
    
    def add_allowed_user(self, user_id: int) -> bool:
        """
        Добавляет пользователя в список разрешённых
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            True если пользователь был добавлен, False если уже существует или ошибка
        """
        if user_id not in self._allowed_users:
            self._allowed_users.append(user_id)
            if self._save_users(self._allowed_users):
                logger.info(f"Пользователь {user_id} добавлен в список разрешённых")
                return True
            else:
                # Откатываем изменения если не удалось сохранить
                self._allowed_users.remove(user_id)
                return False
        return False
    
    def remove_allowed_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя из списка разрешённых
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            True если пользователь был удален, False если не найден или ошибка
        """
        if user_id in self._allowed_users:
            # Сохраняем копию для отката
            old_users = self._allowed_users.copy()
            self._allowed_users.remove(user_id)
            
            if self._save_users(self._allowed_users):
                logger.info(f"Пользователь {user_id} удалён из списка разрешённых")
                return True
            else:
                # Откатываем изменения если не удалось сохранить
                self._allowed_users = old_users
                return False
        return False
    
    def get_allowed_users_list(self) -> List[int]:
        """Возвращает копию списка разрешённых пользователей"""
        return self._allowed_users.copy()
    
    def reload_users(self) -> bool:
        """Перезагружает список пользователей из файла"""
        try:
            self._allowed_users = self._load_users()
            return True
        except Exception as e:
            logger.error(f"Ошибка при перезагрузке пользователей: {e}")
            return False
    
    def get_users_count(self) -> int:
        """Возвращает количество разрешенных пользователей"""
        return len(self._allowed_users)


# Создаем глобальный экземпляр менеджера пользователей
user_manager = UserManager()

# Экспортируем функции для обратной совместимости
def is_allowed_user(user_id: int) -> bool:
    """Проверяет, разрешен ли доступ для пользователя"""
    return user_manager.is_allowed_user(user_id)

def add_allowed_user(user_id: int) -> bool:
    """Добавляет пользователя в список разрешённых"""
    return user_manager.add_allowed_user(user_id)

def remove_allowed_user(user_id: int) -> bool:
    """Удаляет пользователя из списка разрешённых"""
    return user_manager.remove_allowed_user(user_id)

def get_allowed_users_list() -> List[int]:
    """Возвращает список разрешённых пользователей"""
    return user_manager.get_allowed_users_list()

def reload_users() -> bool:
    """Перезагружает список пользователей из файла"""
    return user_manager.reload_users()

def get_users_count() -> int:
    """Возвращает количество разрешенных пользователей"""
    return user_manager.get_users_count() 