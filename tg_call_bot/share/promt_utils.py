from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Константы и базовые пути ---

DEFAULT_MAIN = "Ты HR-эксперт. Проанализируй звонок с водителем и дай профессиональный отчет."
DEFAULT_TEMPLATE = "Стандартный шаблон ответа недоступен."

# корень — как у тебя: на уровень выше текущего файла
_MAIN_PATH = Path(__file__).parent.parent / "promts" / "prompt_main.txt"
_TEMPLATE_PATH = Path(__file__).parent.parent / "promts" / "template_response.txt"
_ENCODING = "utf-8"


# --- Вспомогалки ---

def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def _normalize_text(text: str) -> str:
    # Убираем BOM и нормализуем переносы строк
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    return text.replace("\r\n", "\n").replace("\r", "\n")

def _read_with_default(path: Path, default: str) -> str:
    try:
        if not path.exists():
            _ensure_parent(path)
            path.write_text(default, encoding=_ENCODING)
            logger.info("Создан файл по умолчанию: %s", path)
            return default
        return path.read_text(encoding=_ENCODING)
    except (OSError, UnicodeError) as e:
        logger.error("Ошибка чтения %s: %s", path, e)
        return default

def _write_text(path: Path, content: str) -> bool:
    try:
        _ensure_parent(path)
        path.write_text(_normalize_text(content), encoding=_ENCODING)
        return True
    except (OSError, UnicodeError) as e:
        logger.error("Ошибка записи %s: %s", path, e)
        return False


# --- Публичные функции (тонкие и простые) ---

@lru_cache(maxsize=2)
def get_main_prompt() -> str:
    return _read_with_default(_MAIN_PATH, DEFAULT_MAIN)

@lru_cache(maxsize=2)
def get_response_template() -> str:
    return _read_with_default(_TEMPLATE_PATH, DEFAULT_TEMPLATE)

def get_promt() -> str:
    # не кэшируем склейку отдельно — кэш есть на частях
    return f"{get_main_prompt()}\n\n{get_response_template()}"

def save_main_prompt(content: str) -> bool:
    ok = _write_text(_MAIN_PATH, content)
    if ok:
        # сбрасываем кэш, чтобы сразу видеть изменения
        get_main_prompt.cache_clear()
    return ok

def save_response_template(content: str) -> bool:
    ok = _write_text(_TEMPLATE_PATH, content)
    if ok:
        get_response_template.cache_clear()
    return ok
