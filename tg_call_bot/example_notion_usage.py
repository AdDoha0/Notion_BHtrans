"""
Пример использования функций для работы с Notion
Этот файл можно использовать для тестирования функций
"""

import asyncio
import logging
from services.notion import get_driver_list, add_comment, get_driver_info

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_notion_functions():
    """Тестирует функции работы с Notion"""
    
    try:
        print("🔄 Тестирование функций Notion...")
        print("=" * 50)
        
        # 1. Получаем список водителей
        print("1️⃣ Получение списка водителей...")
        drivers = await get_driver_list()
        
        if drivers:
            print(f"✅ Найдено {len(drivers)} водителей:")
            for i, driver in enumerate(drivers, 1):
                print(f"   {i}. {driver['name']} (ID: {driver['id'][:8]}...)")
        else:
            print("❌ Водители не найдены")
            return
        
        print("\n" + "=" * 50)
        
        # 2. Получаем детальную информацию о первом водителе
        if drivers:
            first_driver_id = drivers[0]["id"]
            print(f"2️⃣ Получение информации о водителе: {drivers[0]['name']}")
            
            driver_info = await get_driver_info(first_driver_id)
            if driver_info:
                print("✅ Информация о водителе:")
                print(f"   Имя: {driver_info['name']}")
                print(f"   Статус: {driver_info['status']}")
                print(f"   О водителе: {driver_info['about_driver']}")
                print(f"   Номер: {driver_info['number']}")
                print(f"   Дата: {driver_info['date']}")
                print(f"   Прицеп: {'Да' if driver_info['trailer'] else 'Нет'}")
                print(f"   Заметки: {driver_info['notes'][:100]}..." if len(driver_info['notes']) > 100 else f"   Заметки: {driver_info['notes']}")
            else:
                print("❌ Не удалось получить информацию о водителе")
        
        print("\n" + "=" * 50)
        
        # 3. Добавляем тестовый комментарий (раскомментируйте для тестирования)
        # ВНИМАНИЕ: Это добавит реальный комментарий в вашу базу данных!
        """
        if drivers:
            test_comment = "Тестовый комментарий из Python скрипта"
            first_driver_id = drivers[0]["id"]
            
            print(f"3️⃣ Добавление комментария к водителю: {drivers[0]['name']}")
            print(f"   Комментарий: {test_comment}")
            
            success = await add_comment(first_driver_id, test_comment)
            if success:
                print("✅ Комментарий успешно добавлен!")
            else:
                print("❌ Не удалось добавить комментарий")
        """
        
        print("\n🎉 Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        logger.error(f"Ошибка при тестировании: {e}")


async def interactive_comment_demo():
    """Интерактивная демонстрация добавления комментариев"""
    
    try:
        print("🚛 Интерактивное добавление комментария")
        print("=" * 50)
        
        # Получаем список водителей
        drivers = await get_driver_list()
        if not drivers:
            print("❌ Водители не найдены")
            return
        
        # Показываем список
        print("Доступные водители:")
        for i, driver in enumerate(drivers, 1):
            print(f"{i}. {driver['name']}")
        
        # Пользователь выбирает водителя (в реальном боте это будет через inline клавиатуру)
        while True:
            try:
                choice = input(f"\nВыберите водителя (1-{len(drivers)}) или 'q' для выхода: ")
                if choice.lower() == 'q':
                    return
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(drivers):
                    selected_driver = drivers[choice_idx]
                    break
                else:
                    print("❌ Неверный выбор, попробуйте снова")
            except ValueError:
                print("❌ Введите число или 'q'")
        
        # Получаем комментарий
        comment = input(f"\nВведите комментарий для {selected_driver['name']}: ")
        if not comment.strip():
            print("❌ Комментарий не может быть пустым")
            return
        
        # Добавляем комментарий
        print("🔄 Добавление комментария...")
        success = await add_comment(selected_driver['id'], comment)
        
        if success:
            print("✅ Комментарий успешно добавлен!")
        else:
            print("❌ Не удалось добавить комментарий")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("Выберите режим:")
    print("1. Тестирование функций (только чтение)")
    print("2. Интерактивное добавление комментария")
    
    try:
        choice = input("Введите 1 или 2: ")
        if choice == "1":
            asyncio.run(test_notion_functions())
        elif choice == "2":
            asyncio.run(interactive_comment_demo())
        else:
            print("❌ Неверный выбор")
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}") 