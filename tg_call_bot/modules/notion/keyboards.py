from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def drivers_kb(drivers: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=(d["name"][:30] + "..." if len(d["name"]) > 30 else d["name"]),
            callback_data=f"driver_select:{d['id']}"
        )]
        for d in drivers
    ]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="driver_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def cancel_comment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="comment_cancel")]
    ])

def info_list_kb(drivers: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=(d["name"][:30] + "..." if len(d["name"]) > 30 else d["name"]),
            callback_data=f"info_show:{d['id']}"
        )] for d in drivers
    ]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="info_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def info_nav_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_drivers")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="info_cancel")]
    ])

def comments_nav_kb(driver_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К информации о водителе", callback_data=f"info_show:{driver_id}")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="info_cancel")]
    ])
