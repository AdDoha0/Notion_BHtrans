import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from notion_client import AsyncClient
import logging

from config import NOTION_KEY, NOTION_DATABASE_ID

# Настройка логирования
logger = logging.getLogger(__name__)

class NotionService:
    """Сервис для работы с базой данных Notion"""
    
    def __init__(self):
        """Инициализация клиента Notion"""
        self.client = AsyncClient(auth=NOTION_KEY)
        self.database_id = NOTION_DATABASE_ID
    
    async def get_names_and_ids(self) -> List[Dict[str, str]]:
        """
        Получает список имен и ID из базы данных Notion
        
        Returns:
            List[Dict[str, str]]: Список словарей с ключами 'id', 'name'
        """
        try:
            # Запрос к базе данных
            response = await self.client.databases.query(
                database_id=self.database_id,
                sorts=[
                    {
                        "property": "Name",
                        "direction": "ascending"
                    }
                ]
            )
            
            results = []
            for page in response["results"]:
                page_id = page["id"]
                
                # Получаем название страницы (Name - это Title property)
                name_property = page["properties"].get("Name", {})
                if name_property.get("type") == "title":
                    title_list = name_property.get("title", [])
                    if title_list:
                        name = "".join([text["plain_text"] for text in title_list])
                    else:
                        name = "Без названия"
                else:
                    name = "Без названия"
                
                results.append({
                    "id": page_id,
                    "name": name
                })
            
            logger.info(f"Получено {len(results)} записей из Notion")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных из Notion: {e}")
            raise Exception(f"Не удалось получить данные из Notion: {e}")
    
    async def add_comment_to_page(self, page_id: str, comment: str) -> bool:
        """
        Создает новый комментарий к странице в Notion
        
        Args:
            page_id (str): ID страницы в Notion
            comment (str): Комментарий для добавления
            
        Returns:
            bool: True если комментарий добавлен успешно, False в противном случае
        """
        try:
            # Создаем новый комментарий к странице
            await self.client.comments.create(
                parent={"page_id": page_id},
                rich_text=[
                    {
                        "text": {
                            "content": comment
                        }
                    }
                ]
            )
            
            logger.info(f"Комментарий создан для страницы {page_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при создании комментария для страницы {page_id}: {e}")
            return False
    
    async def get_page_comments(self, page_id: str) -> List[Dict]:
        """
        Получает список комментариев к странице
        
        Args:
            page_id (str): ID страницы в Notion
            
        Returns:
            List[Dict]: Список комментариев с информацией о времени создания и авторе
        """
        try:
            # Получаем комментарии к странице
            response = await self.client.comments.list(block_id=page_id)
            
            comments = []
            for comment in response.get("results", []):
                comment_data = {
                    "id": comment["id"],
                    "created_time": comment["created_time"],
                    "last_edited_time": comment["last_edited_time"],
                    "created_by": comment.get("created_by", {}),
                    "text": ""
                }
                
                # Извлекаем текст комментария
                rich_text = comment.get("rich_text", [])
                if rich_text:
                    comment_data["text"] = "".join([text.get("plain_text", "") for text in rich_text])
                
                comments.append(comment_data)
            
            logger.info(f"Получено {len(comments)} комментариев для страницы {page_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Ошибка при получении комментариев для страницы {page_id}: {e}")
            return []
    
    async def get_page_details(self, page_id: str) -> Optional[Dict]:
        """
        Получает детальную информацию о странице
        
        Args:
            page_id (str): ID страницы в Notion
            
        Returns:
            Optional[Dict]: Информация о странице или None в случае ошибки
        """
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            properties = page["properties"]
            
            # Извлекаем данные из свойств
            result = {
                "id": page["id"],
                "name": "",
                "status": "",
                "about_driver": "",
                "number": "",
                "date": "",
                "notes": "",
                "trailer": False
            }
            
            # Name (Title)
            if "Name" in properties and properties["Name"]["type"] == "title":
                title_list = properties["Name"].get("title", [])
                result["name"] = "".join([text["plain_text"] for text in title_list])
            
            # Status (Select)
            if "status" in properties and properties["status"]["type"] == "select":
                select_obj = properties["status"].get("select")
                if select_obj:
                    result["status"] = select_obj.get("name", "")
            
            # About in the driver (Rich Text)
            if "About in the driver" in properties and properties["About in the driver"]["type"] == "rich_text":
                rich_text_list = properties["About in the driver"].get("rich_text", [])
                result["about_driver"] = "".join([text["plain_text"] for text in rich_text_list])
            
            # Number (Rich Text)
            if "Number" in properties and properties["Number"]["type"] == "rich_text":
                rich_text_list = properties["Number"].get("rich_text", [])
                result["number"] = "".join([text["plain_text"] for text in rich_text_list])
            
            # Date
            if "Date" in properties and properties["Date"]["type"] == "date":
                date_obj = properties["Date"].get("date")
                if date_obj:
                    result["date"] = date_obj.get("start", "")
            
            # Notes (Rich Text)
            if "Notes" in properties and properties["Notes"]["type"] == "rich_text":
                rich_text_list = properties["Notes"].get("rich_text", [])
                result["notes"] = "".join([text["plain_text"] for text in rich_text_list])
            
            # Trailer (Checkbox)
            if "Trailer" in properties and properties["Trailer"]["type"] == "checkbox":
                result["trailer"] = properties["Trailer"].get("checkbox", False)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при получении деталей страницы {page_id}: {e}")
            return None


# Создаем глобальный экземпляр сервиса
notion_service = NotionService()


# Функции-обертки для удобного использования
async def get_driver_list() -> List[Dict[str, str]]:
    """
    Получает список водителей (имена и ID) для выбора
    
    Returns:
        List[Dict[str, str]]: Список с водителями
    """
    return await notion_service.get_names_and_ids()


async def add_comment(page_id: str, comment: str) -> bool:
    """
    Добавляет комментарий к записи водителя
    
    Args:
        page_id (str): ID записи водителя
        comment (str): Текст комментария
        
    Returns:
        bool: Успешность операции
    """
    return await notion_service.add_comment_to_page(page_id, comment)


async def get_driver_info(page_id: str) -> Optional[Dict]:
    """
    Получает полную информацию о водителе
    
    Args:
        page_id (str): ID записи водителя
        
    Returns:
        Optional[Dict]: Информация о водителе
    """
    return await notion_service.get_page_details(page_id)


async def get_driver_comments(page_id: str) -> List[Dict]:
    """
    Получает комментарии к записи водителя
    
    Args:
        page_id (str): ID записи водителя
        
    Returns:
        List[Dict]: Список комментариев
    """
    return await notion_service.get_page_comments(page_id)